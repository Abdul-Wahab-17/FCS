from fastapi.testclient import TestClient

from src.main import app, repository


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_demo_seed_endpoint_creates_records():
    repository.clear()
    client = TestClient(app)
    response = client.post("/api/demo/seed")
    payload = response.json()
    assert response.status_code == 200
    assert payload["count"] == 4
    assert repository.stats()["total"] == 4
