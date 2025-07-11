"""
Video service for business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.video import Video
from app.models.template import Template
from app.schemas.video import VideoCreate, VideoUpdate
from app.utils.video_processor_bridge import VideoProcessorBridge
from typing import Optional, List, Dict, Any
import os
import uuid
from datetime import datetime
from pathlib import Path


class VideoService:
    
    @staticmethod
    async def create_video(db: AsyncSession, video_data: VideoCreate, user_id: int) -> Video:
        """Create a new video"""
        try:
            # Generate unique filename
            video_id = str(uuid.uuid4())
            
            # Create video record
            db_video = Video(
                title=video_data.title,
                description=video_data.description,
                status="queued",
                metadata={
                    "generation_type": video_data.generation_type,
                    "config": video_data.config,
                    "template_id": video_data.template_id
                },
                user_id=user_id
            )
            
            db.add(db_video)
            await db.commit()
            await db.refresh(db_video)
            
            # Start video processing in background
            # In production, this would be queued as a background task
            try:
                await VideoService.process_video_generation(db, db_video.id, video_data)
            except Exception as e:
                print(f"Background video processing failed: {e}")
                # Don't fail the request, just log the error
            
            return db_video
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create video: {str(e)}"
            )
    
    @staticmethod
    async def get_user_videos(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10) -> List[Video]:
        """Get videos for a user"""
        result = await db.execute(
            select(Video)
            .where(Video.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Video.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_video_by_id(db: AsyncSession, video_id: int, user_id: int) -> Optional[Video]:
        """Get video by ID (only if it belongs to the user)"""
        result = await db.execute(
            select(Video).where(Video.id == video_id, Video.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_video(db: AsyncSession, video_id: int, video_data: VideoUpdate, user_id: int) -> Optional[Video]:
        """Update video information"""
        video = await VideoService.get_video_by_id(db, video_id, user_id)
        if not video:
            return None
        
        # Update fields if provided
        if video_data.title is not None:
            video.title = video_data.title
        
        if video_data.description is not None:
            video.description = video_data.description
        
        if video_data.status is not None:
            video.status = video_data.status
        
        await db.commit()
        await db.refresh(video)
        
        return video
    
    @staticmethod
    async def delete_video(db: AsyncSession, video_id: int, user_id: int) -> bool:
        """Delete a video"""
        video = await VideoService.get_video_by_id(db, video_id, user_id)
        if not video:
            return False
        
        # TODO: Delete actual video files
        # For now, just delete the database record
        await db.delete(video)
        await db.commit()
        
        return True
    
    @staticmethod
    async def get_video_progress(video_id: int) -> dict:
        """Get video processing progress (mock implementation)"""
        # TODO: Implement actual progress tracking
        # For now, return mock data
        return {
            "video_id": video_id,
            "progress": 75.0,
            "stage": "Rendering video",
            "estimated_time_remaining": 30
        }
    
    @staticmethod
    async def process_video_generation(db: AsyncSession, video_id: int, video_data: VideoCreate) -> bool:
        """Process video generation using the video engine"""
        try:
            # Get video record
            video = await db.execute(select(Video).where(Video.id == video_id))
            video = video.scalar_one_or_none()
            if not video:
                return False
            
            # Update status to processing
            video.status = "processing"
            await db.commit()
            
            # Get template if template-based generation
            scenes = []
            if video_data.template_id:
                template_result = await db.execute(
                    select(Template).where(Template.id == video_data.template_id)
                )
                template = template_result.scalar_one_or_none()
                if template:
                    scenes = template.elements.get("scenes", [])
            else:
                # Create scenes from config for other generation types
                scenes = VideoService._create_scenes_from_config(video_data.config)
            
            # Set up file paths
            uploads_dir = Path(__file__).parent.parent.parent / "uploads"
            video_filename = f"video_{video_id}_{uuid.uuid4().hex[:8]}.mp4"
            thumbnail_filename = f"thumb_{video_id}_{uuid.uuid4().hex[:8]}.jpg"
            
            video_path = uploads_dir / "videos" / video_filename
            thumbnail_path = uploads_dir / "thumbnails" / thumbnail_filename
            
            # Initialize video processor bridge
            processor = VideoProcessorBridge()
            
            # Process video
            result = await processor.process_video(
                scenes=scenes,
                config=video_data.config,
                output_path=str(video_path)
            )
            
            if result["success"]:
                # Generate thumbnail
                thumb_result = await processor.generate_thumbnail(
                    str(video_path), 
                    str(thumbnail_path)
                )
                
                # Update video record with results
                video.status = "completed"
                video.file_path = str(video_path)
                video.thumbnail_path = str(thumbnail_path) if thumb_result["success"] else None
                video.duration = result["metadata"]["duration"]
                video.file_size = result["metadata"]["fileSize"]
                video.resolution = result["metadata"]["resolution"]
                video.format = result["metadata"]["format"]
                
                # Update metadata
                if video.metadata:
                    video.metadata.update(result["metadata"])
                else:
                    video.metadata = result["metadata"]
                
                await db.commit()
                return True
            else:
                # Update status to failed
                video.status = "failed"
                if video.metadata:
                    video.metadata["error"] = result.get("error", "Unknown error")
                else:
                    video.metadata = {"error": result.get("error", "Unknown error")}
                await db.commit()
                return False
                
        except Exception as e:
            print(f"Video processing failed: {e}")
            # Update video status to failed
            try:
                video = await db.execute(select(Video).where(Video.id == video_id))
                video = video.scalar_one_or_none()
                if video:
                    video.status = "failed"
                    if video.metadata:
                        video.metadata["error"] = str(e)
                    else:
                        video.metadata = {"error": str(e)}
                    await db.commit()
            except:
                pass
            return False
    
    @staticmethod
    def _create_scenes_from_config(config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create scenes from video configuration for non-template generation"""
        scenes = []
        
        generation_type = config.get("generation_type", "text_to_video")
        
        if generation_type == "text_to_video":
            # Create a simple text scene
            scenes.append({
                "id": "text_scene",
                "type": "main",
                "duration": config.get("duration", 10),
                "elements": [
                    {
                        "id": "main_text",
                        "type": "text",
                        "position": {"x": 50, "y": 50},
                        "size": {"width": 80, "height": 20},
                        "properties": {
                            "text": config.get("textPrompt", "Generated Video"),
                            "fontSize": 32,
                            "fontFamily": "Arial",
                            "color": "#ffffff",
                            "textAlign": "center"
                        }
                    }
                ]
            })
        elif generation_type == "slideshow":
            # Create scenes from images
            images = config.get("images", [])
            duration_per_slide = config.get("duration", 20) / max(len(images), 1)
            
            for i, image_url in enumerate(images):
                scenes.append({
                    "id": f"slide_{i}",
                    "type": "main",
                    "duration": duration_per_slide,
                    "elements": [
                        {
                            "id": f"image_{i}",
                            "type": "image",
                            "position": {"x": 50, "y": 50},
                            "size": {"width": 80, "height": 80},
                            "properties": {
                                "src": image_url
                            }
                        }
                    ]
                })
        else:
            # Default scene for other types
            scenes.append({
                "id": "default_scene",
                "type": "main",
                "duration": config.get("duration", 10),
                "elements": [
                    {
                        "id": "placeholder_text",
                        "type": "text",
                        "position": {"x": 50, "y": 50},
                        "size": {"width": 60, "height": 15},
                        "properties": {
                            "text": "Video Content",
                            "fontSize": 28,
                            "fontFamily": "Arial",
                            "color": "#ffffff",
                            "textAlign": "center"
                        }
                    }
                ]
            })
        
        return scenes
