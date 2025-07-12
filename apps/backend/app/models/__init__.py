"""
Database models
"""

from app.db.database import Base
from app.models.user import User
from app.models.video import Video
from app.models.asset import Asset

# Import template and project models if they exist
try:
    from app.models.template import Template
except ImportError:
    Template = None

try:
    from app.models.project import Project
except ImportError:
    Project = None

__all__ = ["Base", "User", "Video", "Asset"]
if Template:
    __all__.append("Template")
if Project:
    __all__.append("Project")
