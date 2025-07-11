"""
Project model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    settings = Column(JSON, nullable=True)  # Project settings and configuration
    elements = Column(JSON, nullable=True)  # Project elements (customized from template)
    thumbnail_path = Column(String(500), nullable=True)
    status = Column(String(20), default="draft")  # draft, in_progress, completed
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="projects")
    template = relationship("Template")


# Add relationship to User model
from app.models.user import User
User.projects = relationship("Project", back_populates="user")
