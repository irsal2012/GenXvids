"""
User endpoints
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/profile")
async def get_profile():
    """Get user profile"""
    return JSONResponse(
        content={
            "success": True,
            "message": "Get user profile endpoint - Coming soon",
            "data": None
        }
    )


@router.put("/profile")
async def update_profile():
    """Update user profile"""
    return JSONResponse(
        content={
            "success": True,
            "message": "Update user profile endpoint - Coming soon",
            "data": None
        }
    )
