"""
Project endpoints
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/")
async def get_projects():
    """Get user projects"""
    return JSONResponse(
        content={
            "success": True,
            "message": "Get projects endpoint - Coming soon",
            "data": []
        }
    )


@router.post("/")
async def create_project():
    """Create a new project"""
    return JSONResponse(
        content={
            "success": True,
            "message": "Create project endpoint - Coming soon",
            "data": None
        },
        status_code=status.HTTP_201_CREATED
    )


@router.get("/{project_id}")
async def get_project(project_id: int):
    """Get project by ID"""
    return JSONResponse(
        content={
            "success": True,
            "message": f"Get project {project_id} endpoint - Coming soon",
            "data": None
        }
    )


@router.put("/{project_id}")
async def update_project(project_id: int):
    """Update project"""
    return JSONResponse(
        content={
            "success": True,
            "message": f"Update project {project_id} endpoint - Coming soon",
            "data": None
        }
    )


@router.delete("/{project_id}")
async def delete_project(project_id: int):
    """Delete project"""
    return JSONResponse(
        content={
            "success": True,
            "message": f"Delete project {project_id} endpoint - Coming soon",
            "data": None
        }
    )
