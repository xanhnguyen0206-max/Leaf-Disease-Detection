import os
import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.database.seed import seed_database
from app.core.config import settings
from app.services.model_service import get_model_service

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

client = TestClient(app)

TEST_IMG_DIR = os.path.join(settings.PROJECT_ROOT, "training", "datasets", "processed", "tomato_v2", "images", "test")
BACTERIAL_SPOT_IMAGE = os.path.join(TEST_IMG_DIR, "base_Tomato_Bacterial_spot00002_jpg.rf.675e584fd46a1d73482c16d997707954_0068.jpg")
EARLY_BLIGHT_IMAGE = os.path.join(TEST_IMG_DIR, "base_Tomato_Early_blight_00006_jpg.rf.8a58fe93f29624753a5c421ee9ded647_0082.jpg")
LATE_BLIGHT_IMAGE = os.path.join(TEST_IMG_DIR, "base_Tomato_Late_blight_00011_jpg.rf.8cf63f3b102bfdded6463ee7057d3f8c_0160.jpg")
HEALTHY_IMAGE = os.path.join(TEST_IMG_DIR, "ext_heal_H (109)_jpg.rf.W4tL0M9rq4OeeiwbYa37_0027.jpg")

# 1. Health endpoint
def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# 2. Diseases list & detail
def test_diseases_endpoint():
    response = client.get("/api/diseases")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

def test_disease_detail_endpoint():
    for disease_id in ["tomato_early_blight", "tomato_bacterial_spot", "tomato_late_blight"]:
        response = client.get(f"/api/diseases/{disease_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == disease_id
        assert data["plant"] == "Cà chua"

# 3. Care recommendations
def test_care_recommendations_endpoint():
    response = client.get("/api/care/tomato_bacterial_spot")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

# 4. History endpoint
def test_history_endpoint():
    response = client.get("/api/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 5. Bacterial Spot Real Image Prediction (V3)
def test_predict_bacterial_spot_real_image():
    with open(BACTERIAL_SPOT_IMAGE, "rb") as f:
        file_bytes = f.read()

    files = {"file": ("bacterial_spot.jpg", file_bytes, "image/jpeg")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 200
    res = response.json()
    
    assert res["plant"] == "Cà chua"
    assert res["status"] == "detected"
    assert res["primary_disease"] == "Tomato___Bacterial_spot"
    assert res["confidence"] > 0.25
    assert len(res["detections"]) > 0
    assert len(res["recommendations"]) > 0
    assert res["image_url"].startswith("/uploads/")
    assert "id" in res

# 6. Early Blight Real Image Prediction (V3)
def test_predict_early_blight_real_image():
    with open(EARLY_BLIGHT_IMAGE, "rb") as f:
        file_bytes = f.read()

    files = {"file": ("early_blight.jpg", file_bytes, "image/jpeg")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "detected"
    assert res["primary_disease"] == "Tomato___Early_blight"

# 7. Late Blight Real Image Prediction (V3)
def test_predict_late_blight_real_image():
    with open(LATE_BLIGHT_IMAGE, "rb") as f:
        file_bytes = f.read()

    files = {"file": ("late_blight.jpg", file_bytes, "image/jpeg")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "detected"
    assert res["primary_disease"] == "Tomato___Late_blight"

# 8. Healthy Image Prediction (V3 - Safe no_detection handling)
def test_predict_healthy_leaf():
    with open(HEALTHY_IMAGE, "rb") as f:
        file_bytes = f.read()

    files = {"file": ("healthy_leaf.jpg", file_bytes, "image/jpeg")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] in ["detected", "no_detection"]
    if res["status"] == "no_detection":
        assert "không phát hiện" in res["disease"].lower() or "chưa phát hiện" in res["severity"].lower()

# 9. Empty upload file error
def test_predict_empty_upload():
    files = {"file": ("empty.jpg", b"", "image/jpeg")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 400
    assert "trống" in response.json()["detail"].lower()

# 10. Corrupted / non-image data error
def test_predict_invalid_image_data():
    files = {"file": ("fake.jpg", b"corrupted non image bytes header", "image/jpeg")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 400
    assert "bị hỏng" in response.json()["detail"] or "hợp lệ" in response.json()["detail"]

# 11. Unsupported extension error
def test_predict_unsupported_extension():
    files = {"file": ("document.txt", b"plain text", "text/plain")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 400
    assert "không được hỗ trợ" in response.json()["detail"]

# 12. Confidence threshold parameter
def test_predict_confidence_param():
    with open(BACTERIAL_SPOT_IMAGE, "rb") as f:
        file_bytes = f.read()

    files = {"file": ("test_tomato.jpg", file_bytes, "image/jpeg")}
    response = client.post("/api/predict?conf_threshold=0.999", files=files)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "no_detection"
    assert res["confidence"] == 0.0

# 13. Multiple detections & Bounding boxes
def test_multiple_detections_and_bbox_structure():
    with open(BACTERIAL_SPOT_IMAGE, "rb") as f:
        file_bytes = f.read()

    files = {"file": ("multi_det.jpg", file_bytes, "image/jpeg")}
    response = client.post("/api/predict?conf_threshold=0.15", files=files)
    assert response.status_code == 200
    res = response.json()
    
    assert isinstance(res["detections"], list)
    for det in res["detections"]:
        assert "class_id" in det
        assert "disease" in det
        assert "confidence" in det
        assert "bbox" in det
        bbox = det["bbox"]
        assert bbox["x2"] >= bbox["x1"]
        assert bbox["y2"] >= bbox["y1"]

# 14. History persistence and deletion
def test_history_persistence_and_delete():
    # Perform prediction
    with open(BACTERIAL_SPOT_IMAGE, "rb") as f:
        file_bytes = f.read()
    files = {"file": ("history_test.jpg", file_bytes, "image/jpeg")}
    pred_res = client.post("/api/predict", files=files).json()
    item_id = pred_res["id"]

    # Verify present in history list
    res_list = client.get("/api/history").json()
    assert any(h["id"] == item_id for h in res_list)

    # Delete item
    del_res = client.delete(f"/api/history/{item_id}")
    assert del_res.status_code == 204

# 15. Multi-disease grouping structure
def test_detected_diseases_grouping_structure():
    with open(BACTERIAL_SPOT_IMAGE, "rb") as f:
        file_bytes = f.read()
    files = {"file": ("grouping_test.jpg", file_bytes, "image/jpeg")}
    res = client.post("/api/predict", files=files).json()
    assert "detected_diseases" in res
    assert isinstance(res["detected_diseases"], list)
    assert len(res["detected_diseases"]) > 0
    group = res["detected_diseases"][0]
    assert "disease" in group
    assert "disease_name" in group
    assert "max_confidence" in group
    assert "detection_count" in group
    assert "confidence_level" in group
    assert group["confidence_level"] in ["Độ tin cậy cao", "Độ tin cậy trung bình", "Dấu hiệu cần kiểm tra thêm"]

# 16. Rich scientific fields in disease detail
def test_disease_rich_scientific_fields():
    res = client.get("/api/diseases/tomato_bacterial_spot")
    assert res.status_code == 200
    data = res.json()
    assert "scientific_name" in data
    assert "overview" in data
    assert "pathogen" in data
    assert "favorable_conditions" in data
    assert "transmission" in data
    assert "sources" in data
    assert len(data["sources"]) > 0

