"""
Template schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TemplateCategory(str, Enum):
    BUSINESS = "business"
    SOCIAL_MEDIA = "social_media"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    MARKETING = "marketing"
    PERSONAL = "personal"


class AspectRatio(str, Enum):
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    SQUARE = "1:1"
    WIDESCREEN = "21:9"


class VideoStyle(str, Enum):
    CINEMATIC = "cinematic"
    ANIMATED = "animated"
    REALISTIC = "realistic"
    CARTOON = "cartoon"
    MINIMALIST = "minimalist"


class SceneType(str, Enum):
    INTRO = "intro"
    MAIN = "main"
    OUTRO = "outro"
    TRANSITION = "transition"


class ElementType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    SHAPE = "shape"
    EFFECT = "effect"


class AnimationType(str, Enum):
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SLIDE_IN = "slide_in"
    SLIDE_OUT = "slide_out"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    ROTATE = "rotate"
    SCALE = "scale"


class TransitionType(str, Enum):
    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    SLIDE = "slide"


class Position(BaseModel):
    x: float = Field(..., description="X position as percentage (0-100)")
    y: float = Field(..., description="Y position as percentage (0-100)")
    z: Optional[float] = Field(None, description="Z position for layering")


class Size(BaseModel):
    width: float = Field(..., description="Width as percentage (0-100)")
    height: float = Field(..., description="Height as percentage (0-100)")


class Animation(BaseModel):
    type: AnimationType
    duration: float = Field(..., gt=0, description="Animation duration in seconds")
    delay: Optional[float] = Field(0, ge=0, description="Animation delay in seconds")
    easing: Optional[str] = Field("ease-in-out", description="Animation easing function")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Animation-specific properties")


class Transition(BaseModel):
    type: TransitionType
    duration: float = Field(..., gt=0, description="Transition duration in seconds")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Transition-specific properties")


class SceneElement(BaseModel):
    id: str = Field(..., description="Unique element identifier")
    type: ElementType
    position: Position
    size: Size
    properties: Dict[str, Any] = Field(default_factory=dict, description="Element-specific properties")
    animations: Optional[List[Animation]] = Field(default_factory=list, description="Element animations")


class Scene(BaseModel):
    id: str = Field(..., description="Unique scene identifier")
    type: SceneType
    duration: float = Field(..., gt=0, description="Scene duration in seconds")
    elements: List[SceneElement] = Field(..., min_items=1, description="Scene elements")
    transitions: Optional[List[Transition]] = Field(default_factory=list, description="Scene transitions")


class TemplateConfig(BaseModel):
    duration: float = Field(..., gt=0, description="Total template duration in seconds")
    aspect_ratio: AspectRatio
    scenes: List[Scene] = Field(..., min_items=1, description="Template scenes")
    default_style: VideoStyle
    customizable_elements: List[str] = Field(default_factory=list, description="List of customizable element IDs")


class TemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, max_length=1000, description="Template description")
    category: TemplateCategory
    tags: List[str] = Field(default_factory=list, description="Template tags")


class TemplateCreate(TemplateBase):
    elements: TemplateConfig = Field(..., description="Template configuration")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional template settings")
    is_public: bool = Field(True, description="Whether template is publicly available")
    is_featured: bool = Field(False, description="Whether template is featured")


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[TemplateCategory] = None
    tags: Optional[List[str]] = None
    elements: Optional[TemplateConfig] = None
    settings: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None


class TemplateInDB(TemplateBase):
    id: int
    thumbnail_path: Optional[str] = None
    preview_video_path: Optional[str] = None
    duration: Optional[int] = None  # Duration in seconds
    elements: Dict[str, Any]  # JSON field from database
    settings: Optional[Dict[str, Any]] = None
    is_public: bool
    is_featured: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Template(TemplateInDB):
    pass


class TemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: TemplateCategory
    tags: List[str]
    thumbnail_path: Optional[str]
    preview_video_path: Optional[str]
    duration: Optional[int]
    is_public: bool
    is_featured: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime


class TemplateDetailResponse(TemplateResponse):
    elements: TemplateConfig
    settings: Optional[Dict[str, Any]]


class TemplateSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query")
    category: Optional[TemplateCategory] = None
    tags: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    duration_min: Optional[int] = Field(None, ge=1, description="Minimum duration in seconds")
    duration_max: Optional[int] = Field(None, ge=1, description="Maximum duration in seconds")


class TemplateUsageStats(BaseModel):
    template_id: int
    usage_count: int
    last_used: Optional[datetime]
    popular_customizations: Dict[str, Any]
