import pytest
from unittest.mock import patch, Mock, AsyncMock
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

@patch('apps.backend.app.db.database.get_db')
@patch('apps.backend.app.services.template_service.TemplateService.get_template_by_id')
@patch('apps.backend.app.utils.template_customizer.TemplateCustomizer.validate_customizations')
@patch('apps.backend.app.utils.template_customizer.TemplateCustomizer.customize_template')
def test_customize_template(mock_customize_template, mock_validate_customizations, mock_get_template_by_id, mock_get_db, test_app, test_user, test_video, test_template):
    # Mock database session
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    
    # Mock template retrieval
    mock_template_obj = Mock()
    mock_template_obj.id = 1
    mock_template_obj.name = "Test Template"
    mock_template_obj.elements = {
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
    mock_get_template_by_id.return_value = mock_template_obj
    
    # Mock validation
    mock_validate_customizations.return_value = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Mock customization
    mock_customized_config = {
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
                        "properties": {"text": "Custom Title"}
                    }
                ]
            }
        ],
        "default_style": "cinematic"
    }
    mock_customize_template.return_value = mock_customized_config
    
    access_token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "text1": {
            "text": "Custom Title"
        },
        "background_color": "#FF0000"
    }
    response = test_app.post("/api/v1/templates/1/customize", headers=headers, json=payload)
    assert response.status_code == HTTP_200_OK
