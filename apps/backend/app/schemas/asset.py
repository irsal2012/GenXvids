"""
Asset schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FONT = "font"


class AssetCategory(str, Enum):
    BACKGROUNDS = "backgrounds"
    ICONS = "icons"
    MUSIC = "music"
    SOUND_EFFECTS = "sound_effects"
    FONTS = "fonts"
    LOGOS = "logos"
    OVERLAYS = "overlays"
    TRANSITIONS = "transitions"


class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: Optional[AssetCategory] = None
    tags: List[str] = Field(default_factory=list)
    is_public: bool = Field(True)
    is_premium: bool = Field(False)


class AssetCreate(AssetBase):
    original_filename: str
    file_type: AssetType
    mime_type: str
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[AssetCategory] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_premium: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class AssetInDB(AssetBase):
    id: int
    original_filename: str
    file_path: str
    file_type: AssetType
    mime_type: str
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Asset(AssetInDB):
    pass


class AssetResponse(BaseModel):
    id: int
    name: str
    file_path: str
    file_type: AssetType
    mime_type: str
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    category: Optional[AssetCategory] = None
    tags: List[str]
    is_public: bool
    is_premium: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime


class AssetSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query")
    file_type: Optional[AssetType] = None
    category: Optional[AssetCategory] = None
    tags: Optional[List[str]] = None
    is_premium: Optional[bool] = None
    min_width: Optional[int] = Field(None, ge=1)
    max_width: Optional[int] = Field(None, ge=1)
    min_height: Optional[int] = Field(None, ge=1)
    max_height: Optional[int] = Field(None, ge=1)
    min_duration: Optional[float] = Field(None, ge=0)
    max_duration: Optional[float] = Field(None, ge=0)


class AssetUploadResponse(BaseModel):
    success: bool
    message: str
    asset: Optional[AssetResponse] = None
    error: Optional[str] = None


class AssetStats(BaseModel):
    total_assets: int
    by_type: Dict[str, int]
    by_category: Dict[str, int]
    total_size: int  # Total size in bytes
    most_used: Optional[Dict[str, Any]] = None
