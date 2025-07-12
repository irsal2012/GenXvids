import pytest
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from starlette.testclient import TestClient
from apps.backend.main import app

def test_health_endpoint():
    """Test the health check endpoint"""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == HTTP_200_OK
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint"""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == HTTP_200_OK
    assert "message" in response.json()

def test_docs_endpoint():
    """Test the API docs endpoint"""
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == HTTP_200_OK

def test_openapi_endpoint():
    """Test the OpenAPI schema endpoint"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == HTTP_200_OK
    assert "openapi" in response.json()

def test_nonexistent_endpoint():
    """Test that nonexistent endpoints return 404"""
    client = TestClient(app)
    response = client.get("/nonexistent")
    assert response.status_code == HTTP_404_NOT_FOUND
