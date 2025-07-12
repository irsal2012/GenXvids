import os
import sys
import asyncio
import pytest

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'apps'))
sys.path.append(os.path.join(root_path, 'apps', 'backend'))

from starlette.testclient import TestClient
from apps.backend.main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client

@pytest.fixture(scope="module")
def test_user():
    # Create a real JWT token for tests
    from apps.backend.app.utils.auth import create_access_token
    from datetime import timedelta
    
    email = "testuser@example.com"
    access_token = create_access_token(
        data={"sub": email}, 
        expires_delta=timedelta(hours=1)
    )
    
    user_data = {
        "id": 1,
        "email": email,
        "username": "testuser",
        "password": "testpassword",
        "access_token": access_token
    }
    yield user_data

@pytest.fixture(scope="module")
def test_video():
    # Mock video data for tests
    video_data = {
        "id": 1,
        "title": "Test Video",
        "description": "A test video",
        "user_id": 1
    }
    yield video_data

@pytest.fixture(scope="module")
def test_template():
    # Mock template data for tests
    template_data = {
        "id": 1,
        "name": "Test Template",
        "description": "A test template",
        "user_id": 1
    }
    yield template_data
