import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.seed import seed_database

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_diseases_endpoint():
    response = client.get("/api/diseases")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_disease_detail_endpoint():
    response = client.get("/api/diseases/tomato_early_blight")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "tomato_early_blight"
    assert data["plant"] == "Cà chua"

def test_care_recommendations_endpoint():
    response = client.get("/api/care/tomato_early_blight")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_history_endpoint():
    response = client.get("/api/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_predict_mock():
    test_file_content = b"fake image bytes content"
    files = {"file": ("test_leaf.jpg", test_file_content, "image/jpeg")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 200
    res = response.json()
    assert "plant" in res
    assert "disease" in res
    assert "confidence" in res
    assert "image_url" in res
    assert "id" in res

def test_history_delete():
    # First get history list
    res_list = client.get("/api/history").json()
    assert len(res_list) > 0
    item_id = res_list[0]["id"]

    # Delete item
    del_res = client.delete(f"/api/history/{item_id}")
    assert del_res.status_code == 204
