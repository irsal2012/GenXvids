import pytest
from unittest.mock import patch, Mock, AsyncMock
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED

@patch('apps.backend.app.db.database.get_db')
@patch('apps.backend.app.services.user_service.UserService.create_user')
@patch('apps.backend.app.utils.auth.create_tokens')
def test_register(mock_create_tokens, mock_create_user, mock_get_db, test_app):
    # Mock database session
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    
    # Mock the user creation and token generation
    mock_user = Mock()
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_user.username = "testuser"
    mock_user.full_name = None
    mock_user.is_active = True
    mock_user.created_at.isoformat.return_value = "2023-01-01T00:00:00"
    mock_create_user.return_value = mock_user
    mock_create_tokens.return_value = {"access_token": "test_token", "refresh_token": "refresh_token"}
    
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = test_app.post("/api/v1/auth/register", json=payload)
    assert response.status_code == HTTP_201_CREATED
    assert "tokens" in response.json()["data"]

@patch('apps.backend.app.db.database.get_db')
@patch('apps.backend.app.services.user_service.UserService.authenticate_user')
@patch('apps.backend.app.utils.auth.create_tokens')
def test_login(mock_create_tokens, mock_authenticate_user, mock_get_db, test_app):
    # Mock database session
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    
    # Mock successful authentication
    mock_user = Mock()
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_user.username = "testuser"
    mock_user.full_name = None
    mock_user.is_active = True
    mock_user.avatar_url = None
    mock_authenticate_user.return_value = mock_user
    mock_create_tokens.return_value = {"access_token": "test_token", "refresh_token": "refresh_token"}
    
    payload = {
        "email": "test@example.com", 
        "password": "testpassword"
    }
    response = test_app.post("/api/v1/auth/login", json=payload)
    assert response.status_code == HTTP_200_OK
    assert "tokens" in response.json()["data"]

@patch('apps.backend.app.db.database.get_db')
@patch('apps.backend.app.services.user_service.UserService.authenticate_user')
def test_login_invalid_credentials(mock_authenticate_user, mock_get_db, test_app):
    # Mock database session
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    
    # Mock failed authentication
    mock_authenticate_user.return_value = None
    
    payload = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    response = test_app.post("/api/v1/auth/login", json=payload)
    assert response.status_code == HTTP_401_UNAUTHORIZED
