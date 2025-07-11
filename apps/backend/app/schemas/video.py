"""
Video schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class VideoStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUEUED = "queued"


class VideoGenerationType(str, Enum):
    TEXT_TO_VIDEO = "text_to_video"
    TEMPLATE_BASED = "template_based"
    SLIDESHOW = "slideshow"
    SOCIAL_MEDIA = "social_media"
    AI_AVATAR = "ai_avatar"


class VideoQuality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class AspectRatio(str, Enum):
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    SQUARE = "1:1"
    WIDESCREEN = "21:9"


class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None


class VideoCreate(VideoBase):
    generation_type: VideoGenerationType
    config: Dict[str, Any]
    template_id: Optional[int] = None


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[VideoStatus] = None


class VideoInDB(VideoBase):
    id: int
    file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    resolution: Optional[str] = None
    format: Optional[str] = None
    status: VideoStatus
    metadata: Optional[Dict[str, Any]] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Video(VideoInDB):
    pass


class VideoProgress(BaseModel):
    video_id: int
    progress: float
    stage: str
    estimated_time_remaining: Optional[int] = None
