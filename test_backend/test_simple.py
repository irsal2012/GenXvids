import pytest
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED
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

def test_register_real_db():
    """Test user registration with real database"""
    import time
    client = TestClient(app)
    unique_email = f"test{int(time.time())}@example.com"
    unique_username = f"testuser{int(time.time())}"
    
    payload = {
        "email": unique_email,
        "username": unique_username,
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == HTTP_201_CREATED
    assert "tokens" in response.json()["data"]
    assert response.json()["data"]["user"]["email"] == unique_email

def test_login_real_db():
    """Test user login with real database"""
    client = TestClient(app)
    
    # First register a user
    register_payload = {
        "email": "testlogin@example.com",
        "username": "testloginuser",
        "password": "testpassword"
    }
    register_response = client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == HTTP_201_CREATED
    
    # Then try to login
    login_payload = {
        "email": "testlogin@example.com",
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == HTTP_200_OK
    assert "tokens" in response.json()["data"]

def test_login_invalid_credentials_real_db():
    """Test login with invalid credentials"""
    client = TestClient(app)
    payload = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == HTTP_401_UNAUTHORIZED

def test_auth_endpoints_without_token():
    """Test that protected endpoints require authentication"""
    client = TestClient(app)
    
    # Test videos endpoint
    response = client.get("/api/v1/videos/")
    assert response.status_code in [HTTP_401_UNAUTHORIZED, 403]  # Either 401 or 403 is acceptable
    
    # Test templates endpoint  
    response = client.get("/api/v1/templates/")
    assert response.status_code == HTTP_200_OK  # Templates are public
    
    # Test assets endpoint
    response = client.get("/api/v1/assets/")
    assert response.status_code in [HTTP_401_UNAUTHORIZED, 403]  # Either 401 or 403 is acceptable

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
