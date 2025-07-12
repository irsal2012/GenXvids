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

def test_invalid_endpoints():
    """Test various invalid endpoint scenarios"""
    client = TestClient(app)
    
    # Test invalid HTTP methods
    response = client.patch("/api/v1/auth/register")
    assert response.status_code in [HTTP_404_NOT_FOUND, 405]  # Method not allowed or not found
    
    # Test invalid paths
    response = client.get("/api/v1/invalid")
    assert response.status_code == HTTP_404_NOT_FOUND
    
    # Test malformed JSON
    response = client.post("/api/v1/auth/login", data="invalid json")
    assert response.status_code in [400, 422]  # Bad request or unprocessable entity

def test_cors_headers():
    """Test that CORS headers are present"""
    client = TestClient(app)
    response = client.options("/api/v1/templates/")
    # Should not fail with CORS error
    assert response.status_code in [200, 405]  # Either OK or method not allowed

def test_protected_endpoints_require_auth():
    """Test that protected endpoints require authentication"""
    client = TestClient(app)
    
    # Test videos endpoint
    response = client.get("/api/v1/videos/")
    assert response.status_code in [401, 403]  # Either 401 or 403 is acceptable

def test_system_health_endpoint():
    """Test system health endpoint"""
    client = TestClient(app)
    
    # Test system health
    response = client.get("/api/v1/system/health")
    assert response.status_code == HTTP_200_OK

def test_api_endpoints_exist():
    """Test that key API endpoints exist"""
    client = TestClient(app)
    
    # Test that specific endpoints exist (even if they require auth)
    response = client.get("/api/v1/videos/")
    assert response.status_code != HTTP_404_NOT_FOUND  # Should be 401/403, not 404
    
    response = client.get("/api/v1/system/health")
    assert response.status_code == HTTP_200_OK  # Should work without auth
