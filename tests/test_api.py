"""Unit and integration tests for VedaNova REST API endpoints."""
import sys
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    """Verify system health and document readiness probe."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["indexed_documents"] > 0

def test_frontend_serve():
    """Verify that the frontend web application is served at root."""
    res = client.get("/")
    assert res.status_code == 200
    assert "NexaData AI Assistant" in res.text

def test_brand_info_endpoint():
    """Verify company branding and starter prompts metadata."""
    res = client.get("/api/info")
    assert res.status_code == 200
    data = res.json()
    assert data["company_name"] == "NexaData AI"
    assert len(data["prompt_chips"]) >= 3

def test_company_chat_mode():
    """Verify RAG-grounded response in company mode."""
    res = client.post("/api/chat", json={
        "message": "What are your wellness services?",
        "mode": "company"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "company"
    assert len(data["sources"]) > 0
    assert "timestamp" in data

def test_general_chat_mode():
    """Verify response in general AI mode."""
    res = client.post("/api/chat", json={
        "message": "What is machine learning?",
        "mode": "general"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "general"

def test_invalid_request_validation():
    """Verify 422 validation on invalid mode parameter."""
    res = client.post("/api/chat", json={
        "message": "Hello",
        "mode": "unsupported_mode"
    })
    assert res.status_code == 422

if __name__ == "__main__":
    test_health_endpoint()
    test_frontend_serve()
    test_brand_info_endpoint()
    test_company_chat_mode()
    test_general_chat_mode()
    test_invalid_request_validation()
    print("All API integration tests passed successfully.")
