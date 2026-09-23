import os
import io
import pytest
from PIL import Image
from app.services.yolo_model_service import YOLOModelService
from app.services.model_service import MockModelService, get_model_service
from app.core.config import settings

TEST_IMG_DIR = os.path.join(settings.PROJECT_ROOT, "training", "datasets", "processed", "tomato_v2", "images", "test")
BACTERIAL_SPOT_IMAGE = os.path.join(TEST_IMG_DIR, "base_Tomato_Bacterial_spot00002_jpg.rf.675e584fd46a1d73482c16d997707954_0068.jpg")
EARLY_BLIGHT_IMAGE = os.path.join(TEST_IMG_DIR, "base_Tomato_Early_blight_00006_jpg.rf.8a58fe93f29624753a5c421ee9ded647_0082.jpg")
LATE_BLIGHT_IMAGE = os.path.join(TEST_IMG_DIR, "base_Tomato_Late_blight_00011_jpg.rf.8cf63f3b102bfdded6463ee7057d3f8c_0160.jpg")
HEALTHY_IMAGE = os.path.join(TEST_IMG_DIR, "ext_heal_H (109)_jpg.rf.W4tL0M9rq4OeeiwbYa37_0027.jpg")

def test_v4_model_loading_success():
    """Verify that YOLOModelService loads the V4 model into memory with 6 classes at 640x640."""
    service = YOLOModelService(model_path=settings.MODEL_PATH, device="cpu")
    assert service.model is not None
    assert len(service.classes) == 6
    assert service.classes[0] == "Tomato___Bacterial_spot"
    assert service.classes[1] == "Tomato___Early_blight"
    assert service.classes[2] == "Tomato___Late_blight"
    assert service.classes[3] == "Tomato___Septoria_leaf_spot"
    assert service.classes[4] == "Tomato___Leaf_mold"
    assert service.classes[5] == "Tomato___Powdery_mildew"
    assert service.imgsz == 640

def test_model_loading_missing_file():
    """Verify that YOLOModelService fails clearly with FileNotFoundError when model path does not exist."""
    with pytest.raises(FileNotFoundError) as exc_info:
        YOLOModelService(model_path="non_existent_path/model.pt")
    assert "YOLO model file not found" in str(exc_info.value)

def test_v3_inference_bacterial_spot():
    """Verify V3 inference accurately detects Bacterial Spot on real test image."""
    assert os.path.exists(BACTERIAL_SPOT_IMAGE), f"Test image not found at {BACTERIAL_SPOT_IMAGE}"
    service = YOLOModelService(model_path=settings.MODEL_PATH, default_conf=0.25, device="cpu")
    
    result = service.predict(BACTERIAL_SPOT_IMAGE)
    assert result["plant"] == "Cà chua"
    assert result["status"] == "detected"
    assert result["primary_disease"] == "Tomato___Bacterial_spot"
    assert result["confidence"] > 0.25
    assert len(result["detections"]) > 0

    first_det = result["detections"][0]
    assert first_det["class_id"] == 0
    assert first_det["disease"] == "Tomato___Bacterial_spot"
    assert all(k in first_det["bbox"] for k in ("x1", "y1", "x2", "y2"))

def test_v3_inference_early_blight():
    """Verify V3 inference detects Early Blight."""
    assert os.path.exists(EARLY_BLIGHT_IMAGE)
    service = YOLOModelService(model_path=settings.MODEL_PATH, default_conf=0.25, device="cpu")
    result = service.predict(EARLY_BLIGHT_IMAGE)
    assert result["status"] == "detected"
    assert result["primary_disease"] == "Tomato___Early_blight"

def test_v3_inference_late_blight():
    """Verify V3 inference detects Late Blight."""
    assert os.path.exists(LATE_BLIGHT_IMAGE)
    service = YOLOModelService(model_path=settings.MODEL_PATH, default_conf=0.25, device="cpu")
    result = service.predict(LATE_BLIGHT_IMAGE)
    assert result["status"] == "detected"
    assert result["primary_disease"] == "Tomato___Late_blight"

def test_v3_confidence_threshold():
    """Verify confidence threshold filtering."""
    service = YOLOModelService(model_path=settings.MODEL_PATH, device="cpu")
    res_low = service.predict(BACTERIAL_SPOT_IMAGE, conf_threshold=0.10)
    res_high = service.predict(BACTERIAL_SPOT_IMAGE, conf_threshold=0.999)
    
    assert len(res_low["detections"]) >= len(res_high["detections"])
    assert res_high["status"] == "no_detection"
    assert res_high["confidence"] == 0.0

def test_v3_no_detection_on_blank_image(tmp_path):
    """Verify no_detection status when no lesions exist on plain image."""
    blank_img_path = str(tmp_path / "blank.jpg")
    img = Image.new("RGB", (640, 640), color=(255, 255, 255))
    img.save(blank_img_path)

    service = YOLOModelService(model_path=settings.MODEL_PATH, default_conf=0.25, device="cpu")
    result = service.predict(blank_img_path)

    assert result["status"] == "no_detection"
    assert result["confidence"] == 0.0
    assert result["detections"] == []

def test_postprocess_detections_filters_invalid_boxes():
    """Verify postprocess_detections removes degenerate bounding boxes."""
    service = YOLOModelService(model_path=settings.MODEL_PATH, device="cpu")
    sample_dets = [
        {"class_id": 0, "disease": "Tomato___Bacterial_spot", "confidence": 0.85, "bbox": {"x1": 10, "y1": 10, "x2": 50, "y2": 50}},
        {"class_id": 0, "disease": "Tomato___Bacterial_spot", "confidence": 0.50, "bbox": {"x1": 50, "y1": 50, "x2": 10, "y2": 50}}, # inverted x
        {"class_id": 1, "disease": "Tomato___Early_blight", "confidence": 0.60, "bbox": {"x1": 20, "y1": 20, "x2": 20, "y2": 80}}, # 0-width
    ]
    filtered = service.postprocess_detections(sample_dets)
    assert len(filtered) == 1
    assert filtered[0]["confidence"] == 0.85

def test_model_version_switching_v3_v2_mock():
    """Verify switching between V3, V2 backup, and Mock service."""
    # V3 Service
    v3_path = os.path.join(settings.PROJECT_ROOT, "model", "tomato_v3", "best.pt")
    v3_svc = YOLOModelService(model_path=v3_path, imgsz=640, device="cpu")
    assert v3_svc.imgsz == 640

    # V2 Backup Service
    v2_path = os.path.join(settings.PROJECT_ROOT, "model", "tomato_v2", "best.pt")
    assert os.path.exists(v2_path), "Backup V2 model must exist"
    v2_svc = YOLOModelService(model_path=v2_path, imgsz=384, device="cpu")
    assert v2_svc.imgsz == 384

    # Mock Service
    mock_svc = MockModelService()
    mock_res = mock_svc.predict("dummy_path")
    assert "plant" in mock_res
    assert "confidence" in mock_res
