"""
Template endpoints
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/")
async def get_templates():
    """Get all templates"""
    return JSONResponse(
        content={
            "success": True,
            "message": "Get templates endpoint - Coming soon",
            "data": []
        }
    )


@router.post("/")
async def create_template():
    """Create a new template"""
    return JSONResponse(
        content={
            "success": True,
            "message": "Create template endpoint - Coming soon",
            "data": None
        },
        status_code=status.HTTP_201_CREATED
    )


@router.get("/{template_id}")
async def get_template(template_id: int):
    """Get template by ID"""
    return JSONResponse(
        content={
            "success": True,
            "message": f"Get template {template_id} endpoint - Coming soon",
            "data": None
        }
    )
