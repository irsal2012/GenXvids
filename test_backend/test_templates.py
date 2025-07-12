import pytest
from unittest.mock import patch, Mock, AsyncMock
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

@patch('apps.backend.app.db.database.get_db')
@patch('apps.backend.app.services.template_service.TemplateService.create_template')
def test_create_template(mock_create_template, mock_get_db, test_app, test_user):
    # Mock database session
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    
    # Mock the template creation
    mock_template = Mock()
    mock_template.id = 1
    mock_template.name = "Test Template"
    mock_template.description = "This is a test template"
    mock_template.category = "business"
    mock_template.tags = ["test"]
    mock_template.duration = 10
    mock_template.is_public = True
    mock_template.is_featured = False
    mock_template.usage_count = 0
    mock_template.created_at.isoformat.return_value = "2023-01-01T00:00:00"
    mock_template.updated_at.isoformat.return_value = "2023-01-01T00:00:00"
    mock_create_template.return_value = mock_template
    
    access_token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "name": "Test Template",
        "description": "This is a test template",
        "category": "business",
        "tags": ["test"],
        "elements": {
            "duration": 10.0,
            "aspect_ratio": "16:9",
            "scenes": [
                {
                    "id": "scene1",
                    "type": "main",
                    "duration": 10.0,
                    "elements": [
                        {
                            "id": "text1",
                            "type": "text",
                            "position": {"x": 50, "y": 50},
                            "size": {"width": 80, "height": 20},
                            "properties": {"text": "Hello World"}
                        }
                    ]
                }
            ],
            "default_style": "cinematic"
        }
    }
    response = test_app.post("/api/v1/templates/", headers=headers, json=payload)
    assert response.status_code == HTTP_201_CREATED

@patch('apps.backend.app.db.database.get_db')
@patch('apps.backend.app.services.template_service.TemplateService.get_template_by_id')
def test_get_nonexistent_template(mock_get_template_by_id, mock_get_db, test_app, test_user):
    # Mock database session
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    
    # Mock template not found
    mock_get_template_by_id.return_value = None
    
    access_token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = test_app.get("/api/v1/templates/999", headers=headers)
    assert response.status_code == HTTP_404_NOT_FOUND
