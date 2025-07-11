"""
Asset endpoints for file management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.asset import (
    AssetResponse,
    AssetUpdate,
    AssetSearchRequest,
    AssetType,
    AssetCategory,
    AssetUploadResponse
)
from app.services.asset_service import AssetService
from typing import List, Optional

router = APIRouter()


@router.get("/", response_model=dict)
async def get_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    file_type: Optional[AssetType] = None,
    category: Optional[AssetCategory] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    search: Optional[str] = None,
    is_premium: Optional[bool] = None,
    min_width: Optional[int] = Query(None, ge=1),
    max_width: Optional[int] = Query(None, ge=1),
    min_height: Optional[int] = Query(None, ge=1),
    max_height: Optional[int] = Query(None, ge=1),
    min_duration: Optional[float] = Query(None, ge=0),
    max_duration: Optional[float] = Query(None, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get assets with filtering options"""
    try:
        # Parse tags if provided
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Create search parameters
        search_params = AssetSearchRequest(
            query=search,
            file_type=file_type,
            category=category,
            tags=tag_list if tag_list else None,
            is_premium=is_premium,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            min_duration=min_duration,
            max_duration=max_duration
        )
        
        assets = await AssetService.get_assets(db, skip, limit, search_params)
        
        asset_data = []
        for asset in assets:
            asset_data.append({
                "id": asset.id,
                "name": asset.name,
                "file_path": asset.file_path,
                "file_type": asset.file_type,
                "mime_type": asset.mime_type,
                "file_size": asset.file_size,
                "width": asset.width,
                "height": asset.height,
                "duration": asset.duration,
                "category": asset.category,
                "tags": asset.tags or [],
                "is_public": asset.is_public,
                "is_premium": asset.is_premium,
                "usage_count": asset.usage_count,
                "created_at": asset.created_at.isoformat(),
                "updated_at": asset.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "message": "Assets retrieved successfully",
            "data": asset_data,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": len(asset_data)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assets: {str(e)}"
        )


@router.post("/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    category: Optional[AssetCategory] = Form(None),
    tags: Optional[str] = Form(None, description="Comma-separated tags"),
    db: AsyncSession = Depends(get_db)
):
    """Upload a new asset file"""
    try:
        # Parse tags if provided
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Upload asset
        asset = await AssetService.upload_asset(
            db=db,
            file=file,
            name=name,
            category=category,
            tags=tag_list
        )
        
        return {
            "success": True,
            "message": "Asset uploaded successfully",
            "data": {
                "id": asset.id,
                "name": asset.name,
                "file_path": asset.file_path,
                "file_type": asset.file_type,
                "mime_type": asset.mime_type,
                "file_size": asset.file_size,
                "width": asset.width,
                "height": asset.height,
                "duration": asset.duration,
                "category": asset.category,
                "tags": asset.tags or [],
                "created_at": asset.created_at.isoformat()
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Asset upload failed: {str(e)}"
        )


@router.get("/types/{file_type}", response_model=dict)
async def get_assets_by_type(
    file_type: AssetType,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get assets by file type"""
    try:
        assets = await AssetService.get_assets_by_type(db, file_type, limit)
        
        asset_data = []
        for asset in assets:
            asset_data.append({
                "id": asset.id,
                "name": asset.name,
                "file_path": asset.file_path,
                "file_type": asset.file_type,
                "mime_type": asset.mime_type,
                "file_size": asset.file_size,
                "width": asset.width,
                "height": asset.height,
                "duration": asset.duration,
                "category": asset.category,
                "tags": asset.tags or [],
                "usage_count": asset.usage_count,
                "created_at": asset.created_at.isoformat()
            })
        
        return {
            "success": True,
            "message": f"Assets of type {file_type.value} retrieved successfully",
            "data": asset_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assets by type: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_asset_stats(db: AsyncSession = Depends(get_db)):
    """Get asset statistics"""
    try:
        stats = await AssetService.get_asset_stats(db)
        
        return {
            "success": True,
            "message": "Asset statistics retrieved successfully",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve asset statistics: {str(e)}"
        )


@router.get("/{asset_id}", response_model=dict)
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get asset by ID"""
    try:
        asset = await AssetService.get_asset_by_id(db, asset_id)
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        return {
            "success": True,
            "message": "Asset retrieved successfully",
            "data": {
                "id": asset.id,
                "name": asset.name,
                "original_filename": asset.original_filename,
                "file_path": asset.file_path,
                "file_type": asset.file_type,
                "mime_type": asset.mime_type,
                "file_size": asset.file_size,
                "width": asset.width,
                "height": asset.height,
                "duration": asset.duration,
                "category": asset.category,
                "tags": asset.tags or [],
                "metadata": asset.metadata,
                "is_public": asset.is_public,
                "is_premium": asset.is_premium,
                "usage_count": asset.usage_count,
                "created_at": asset.created_at.isoformat(),
                "updated_at": asset.updated_at.isoformat()
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve asset: {str(e)}"
        )


@router.put("/{asset_id}", response_model=dict)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update asset information"""
    try:
        asset = await AssetService.update_asset(db, asset_id, asset_data)
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        return {
            "success": True,
            "message": "Asset updated successfully",
            "data": {
                "id": asset.id,
                "name": asset.name,
                "category": asset.category,
                "tags": asset.tags or [],
                "is_public": asset.is_public,
                "is_premium": asset.is_premium,
                "updated_at": asset.updated_at.isoformat()
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update asset: {str(e)}"
        )


@router.delete("/{asset_id}", response_model=dict)
async def delete_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete asset"""
    try:
        success = await AssetService.delete_asset(db, asset_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        return {
            "success": True,
            "message": "Asset deleted successfully",
            "data": None
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete asset: {str(e)}"
        )


@router.post("/{asset_id}/use", response_model=dict)
async def use_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark asset as used (increment usage count)"""
    try:
        success = await AssetService.increment_usage_count(db, asset_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        return {
            "success": True,
            "message": "Asset usage recorded successfully",
            "data": None
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record asset usage: {str(e)}"
        )
