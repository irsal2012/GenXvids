"""
Main API router for v1
"""

from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, videos, templates, projects

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
