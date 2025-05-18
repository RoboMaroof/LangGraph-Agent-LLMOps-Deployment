from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_agent_invoke_minimal():
    response = client.post("/agent/invoke", json={"input": "What is LangGraph?"})
    assert response.status_code == 200
    assert "final_output" in response.json()

def test_agent_invoke_invalid():
    response = client.post("/agent/invoke", json={"input": {}})
    assert response.status_code == 400
