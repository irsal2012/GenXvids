"""
Video endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.schemas.video import VideoCreate, VideoUpdate, Video
from app.schemas.user import User
from app.services.video_service import VideoService
from app.api.api_v1.endpoints.auth import get_current_user
from app.models.video import Video as VideoModel
from typing import List
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=dict)
async def get_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user videos"""
    try:
        videos = await VideoService.get_user_videos(db, current_user.id, skip, limit)
        
        video_data = []
        for video in videos:
            video_data.append({
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "status": video.status,
                "file_path": video.file_path,
                "thumbnail_path": video.thumbnail_path,
                "duration": video.duration,
                "file_size": video.file_size,
                "resolution": video.resolution,
                "format": video.format,
                "metadata": video.video_metadata,
                "created_at": video.created_at.isoformat(),
                "updated_at": video.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "message": "Videos retrieved successfully",
            "data": video_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve videos: {str(e)}"
        )


@router.post("/generate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_video(
    video_data: VideoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a new video"""
    try:
        logger.info(f"Starting video generation for user {current_user.id}")
        logger.info(f"Video data: {video_data.dict()}")
        
        # Create video record
        video = await VideoService.create_video(db, video_data, current_user.id)
        
        logger.info(f"Video record created successfully with ID: {video.id}")
        
        return {
            "success": True,
            "message": "Video generation started",
            "data": {
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "status": video.status,
                "metadata": video.video_metadata,
                "created_at": video.created_at.isoformat()
            }
        }
    except HTTPException as e:
        logger.error(f"HTTP error during video generation: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during video generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video generation failed: {str(e)}"
        )


@router.get("/{video_id}", response_model=dict)
async def get_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get video by ID"""
    try:
        video = await VideoService.get_video_by_id(db, video_id, current_user.id)
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        return {
            "success": True,
            "message": "Video retrieved successfully",
            "data": {
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "status": video.status,
                "file_path": video.file_path,
                "thumbnail_path": video.thumbnail_path,
                "duration": video.duration,
                "file_size": video.file_size,
                "resolution": video.resolution,
                "format": video.format,
                "metadata": video.video_metadata,
                "created_at": video.created_at.isoformat(),
                "updated_at": video.updated_at.isoformat()
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve video: {str(e)}"
        )


@router.put("/{video_id}", response_model=dict)
async def update_video(
    video_id: int,
    video_data: VideoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update video information"""
    try:
        video = await VideoService.update_video(db, video_id, video_data, current_user.id)
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        return {
            "success": True,
            "message": "Video updated successfully",
            "data": {
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "status": video.status,
                "updated_at": video.updated_at.isoformat()
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update video: {str(e)}"
        )


@router.delete("/{video_id}", response_model=dict)
async def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete video"""
    try:
        success = await VideoService.delete_video(db, video_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        return {
            "success": True,
            "message": "Video deleted successfully",
            "data": None
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete video: {str(e)}"
        )


@router.get("/{video_id}/progress", response_model=dict)
async def get_video_progress(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get video processing progress"""
    try:
        # Verify video belongs to user
        video = await VideoService.get_video_by_id(db, video_id, current_user.id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        # Get progress
        progress = await VideoService.get_video_progress(video_id)
        
        return {
            "success": True,
            "message": "Progress retrieved successfully",
            "data": progress
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress: {str(e)}"
        )


@router.post("/test-generate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def test_generate_video(
    video_data: VideoCreate,
    db: AsyncSession = Depends(get_db)
):
    """Test video generation without authentication (for debugging)"""
    try:
        logger.info(f"Starting test video generation")
        logger.info(f"Video data: {video_data.dict()}")
        
        # Create video record with a test user ID (1)
        video = await VideoService.create_video(db, video_data, user_id=1)
        
        logger.info(f"Test video record created successfully with ID: {video.id}")
        
        return {
            "success": True,
            "message": "Test video generation started",
            "data": {
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "status": video.status,
                "metadata": video.video_metadata,
                "created_at": video.created_at.isoformat()
            }
        }
    except HTTPException as e:
        logger.error(f"HTTP error during test video generation: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during test video generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test video generation failed: {str(e)}"
        )


@router.get("/{video_id}/download")
async def download_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download or view the generated video file"""
    try:
        # Get video record
        video = await VideoService.get_video_by_id(db, video_id, current_user.id)
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        if not video.file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video file not found"
            )
        
        # Check if file exists
        file_path = Path(video.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video file does not exist on disk"
            )
        
        # Determine media type based on file extension
        if file_path.suffix.lower() == '.html':
            media_type = "text/html"
        elif file_path.suffix.lower() == '.mp4':
            media_type = "video/mp4"
        else:
            media_type = "application/octet-stream"
        
        # Return file
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=f"{video.title}_{video.id}{file_path.suffix}"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error serving video file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serve video file: {str(e)}"
        )


@router.get("/{video_id}/view")
async def view_video(
    video_id: int,
    db: AsyncSession = Depends(get_db)
):
    """View video without authentication (for HTML previews)"""
    try:
        # Get video record (no auth required for viewing)
        result = await db.execute(
            select(VideoModel).where(VideoModel.id == video_id)
        )
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        if not video.file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video file not found"
            )
        
        # Check if file exists
        file_path = Path(video.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video file does not exist on disk"
            )
        
        # Only serve HTML files through this endpoint
        if file_path.suffix.lower() != '.html':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This endpoint only serves HTML preview files"
            )
        
        # Return HTML file
        return FileResponse(
            path=str(file_path),
            media_type="text/html",
            filename=f"{video.title}_{video.id}.html"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error serving video preview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serve video preview: {str(e)}"
        )
