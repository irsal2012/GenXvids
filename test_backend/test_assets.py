import pytest
from unittest.mock import patch, Mock, AsyncMock
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND
import io

@patch('apps.backend.app.db.database.get_db')
@patch('apps.backend.app.services.asset_service.AssetService.upload_asset')
def test_create_asset(mock_upload_asset, mock_get_db, test_app, test_user):
    # Mock database session
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    
    # Mock the asset upload
    mock_asset = Mock()
    mock_asset.id = 1
    mock_asset.name = "Test Asset"
    mock_asset.original_filename = "sample.png"
    mock_asset.file_path = "/uploads/test_asset.png"
    mock_asset.file_type = "image"
    mock_upload_asset.return_value = mock_asset
    
    access_token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create a mock file
    file_content = b"fake image content"
    files = {"file": ("sample.png", io.BytesIO(file_content), "image/png")}
    payload = {
        "name": "Test Asset"
    }
    
    response = test_app.post("/api/v1/assets/upload", headers=headers, data=payload, files=files)
    assert response.status_code == HTTP_201_CREATED

@patch('apps.backend.app.db.database.get_db')
@patch('apps.backend.app.services.asset_service.AssetService.get_asset_by_id')
def test_get_nonexistent_asset(mock_get_asset_by_id, mock_get_db, test_app, test_user):
    # Mock database session
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    
    # Mock asset not found
    mock_get_asset_by_id.return_value = None
    
    access_token = test_user["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = test_app.get("/api/v1/assets/999", headers=headers)
    assert response.status_code == HTTP_404_NOT_FOUND
