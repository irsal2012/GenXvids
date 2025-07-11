"""
Template model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)  # Array of tags
    thumbnail_path = Column(String(500), nullable=True)
    preview_video_path = Column(String(500), nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    elements = Column(JSON, nullable=False)  # Template elements configuration
    settings = Column(JSON, nullable=True)  # Template settings
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
