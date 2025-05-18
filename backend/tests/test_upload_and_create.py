from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_manual_ingest_invalid():
    response = client.post("/vectordb/create", json={
        "source_type": "unknown", "source_path": "/does/not/exist"
    })
    assert response.status_code == 200
    assert "error" in response.json()
