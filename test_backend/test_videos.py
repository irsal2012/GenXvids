import pytest
from unittest.mock import patch, Mock, AsyncMock
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

@patch('apps.backend.app.db.database.get_db')
@patch('apps.backend.app.api.api_v1.endpoints.auth.get_current_user')
@patch('apps.backend.app.services.video_service.VideoService.create_video')
def test_create_video(mock_create_video, mock_get_current_user, mock_get_db, test_app, test_user):
    # Mock database session
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    
    # Mock current user
    mock_user = Mock()
    mock_user.id = test_user["id"]
    mock_user.email = test_user["email"]
    mock_user.username = test_user["username"]
    mock_get_current_user.return_value = mock_user
    
    # Mock the video creation
    mock_video = Mock()
    mock_video.id = 1
    mock_video.title = "Test Video"
    mock_video.description = "This is a test video"
    mock_video.status = "queued"
    mock_video.metadata = {}
    mock_video.created_at.isoformat.return_value = "2023-01-01T00:00:00"
    mock_create_video.return_value = mock_video
    
    access_token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "title": "Test Video",
        "description": "This is a test video",
        "generation_type": "text_to_video",
        "config": {
            "textPrompt": "A beautiful sunset",
            "duration": 10
        }
    }
    response = test_app.post("/api/v1/videos/generate", headers=headers, json=payload)
    assert response.status_code == HTTP_201_CREATED

@patch('apps.backend.app.db.database.get_db')
@patch('apps.backend.app.services.video_service.VideoService.get_video_by_id')
def test_get_nonexistent_video(mock_get_video_by_id, mock_get_db, test_app, test_user):
    # Mock database session
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    
    # Mock video not found
    mock_get_video_by_id.return_value = None
    
    access_token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = test_app.get("/api/v1/videos/999", headers=headers)
    assert response.status_code == HTTP_404_NOT_FOUND
