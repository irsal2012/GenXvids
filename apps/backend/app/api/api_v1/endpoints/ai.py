"""
AI-powered endpoints using OpenAI
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.services.openai_service import openai_service
from app.api.api_v1.endpoints.auth import get_current_user
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class TextGenerationRequest(BaseModel):
    """Request model for text generation"""
    prompt: str = Field(..., description="The prompt for text generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(None, description="Sampling temperature (0.0 to 1.0)")
    system_message: Optional[str] = Field(None, description="Optional system message")


class VideoScriptRequest(BaseModel):
    """Request model for video script generation"""
    topic: str = Field(..., description="The video topic")
    duration: int = Field(60, description="Target duration in seconds")
    style: str = Field("engaging", description="Script style (engaging, professional, casual, etc.)")


class SceneDescriptionRequest(BaseModel):
    """Request model for scene description generation"""
    script_segment: str = Field(..., description="The script text to create visuals for")
    visual_style: str = Field("modern", description="Visual style preference")


class ImagePromptRequest(BaseModel):
    """Request model for image prompt generation"""
    description: str = Field(..., description="Basic description of desired image")
    style: str = Field("photorealistic", description="Image style preference")


class ContentAnalysisRequest(BaseModel):
    """Request model for content analysis"""
    content: str = Field(..., description="Content to analyze")
    analysis_type: str = Field("general", description="Type of analysis (sentiment, topics, quality, etc.)")


@router.post("/generate-text")
async def generate_text(
    request: TextGenerationRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate text using OpenAI
    """
    try:
        result = await openai_service.generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system_message=request.system_message
        )
        
        if result is None:
            raise HTTPException(
                status_code=503,
                detail="AI service unavailable or failed to generate text"
            )
        
        return {
            "success": True,
            "generated_text": result,
            "prompt": request.prompt,
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"Error in generate_text endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate text: {str(e)}"
        )


@router.post("/generate-video-script")
async def generate_video_script(
    request: VideoScriptRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate a video script for the given topic
    """
    try:
        result = await openai_service.generate_video_script(
            topic=request.topic,
            duration=request.duration,
            style=request.style
        )
        
        if result is None:
            raise HTTPException(
                status_code=503,
                detail="AI service unavailable or failed to generate script"
            )
        
        return {
            "success": True,
            "script": result,
            "topic": request.topic,
            "duration": request.duration,
            "style": request.style,
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"Error in generate_video_script endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video script: {str(e)}"
        )


@router.post("/generate-scene-description")
async def generate_scene_description(
    request: SceneDescriptionRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate visual scene descriptions for video segments
    """
    try:
        result = await openai_service.generate_scene_description(
            script_segment=request.script_segment,
            visual_style=request.visual_style
        )
        
        if result is None:
            raise HTTPException(
                status_code=503,
                detail="AI service unavailable or failed to generate scene description"
            )
        
        return {
            "success": True,
            "scene_description": result,
            "script_segment": request.script_segment,
            "visual_style": request.visual_style,
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"Error in generate_scene_description endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate scene description: {str(e)}"
        )


@router.post("/generate-image-prompt")
async def generate_image_prompt(
    request: ImagePromptRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate optimized prompts for image generation
    """
    try:
        result = await openai_service.generate_image_prompt(
            description=request.description,
            style=request.style
        )
        
        if result is None:
            raise HTTPException(
                status_code=503,
                detail="AI service unavailable or failed to generate image prompt"
            )
        
        return {
            "success": True,
            "optimized_prompt": result,
            "original_description": request.description,
            "style": request.style,
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"Error in generate_image_prompt endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate image prompt: {str(e)}"
        )


@router.post("/analyze-content")
async def analyze_content(
    request: ContentAnalysisRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Analyze content for various purposes
    """
    try:
        result = await openai_service.analyze_content(
            content=request.content,
            analysis_type=request.analysis_type
        )
        
        if result is None:
            raise HTTPException(
                status_code=503,
                detail="AI service unavailable or failed to analyze content"
            )
        
        return {
            "success": True,
            "analysis": result,
            "content_length": len(request.content),
            "analysis_type": request.analysis_type,
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_content endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze content: {str(e)}"
        )


@router.get("/health")
async def ai_health_check() -> Dict[str, Any]:
    """
    Check the health of the AI service
    """
    try:
        health_status = await openai_service.health_check()
        
        return {
            "service": "OpenAI",
            "timestamp": "2025-01-11T21:42:00Z",
            **health_status
        }
        
    except Exception as e:
        logger.error(f"Error in AI health check: {e}")
        return {
            "service": "OpenAI",
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "timestamp": "2025-01-11T21:42:00Z"
        }


@router.get("/capabilities")
async def get_ai_capabilities() -> Dict[str, Any]:
    """
    Get information about available AI capabilities
    """
    return {
        "service": "Azure OpenAI",
        "capabilities": [
            {
                "name": "Text Generation",
                "description": "Generate text based on prompts",
                "endpoint": "/ai/generate-text"
            },
            {
                "name": "Video Script Generation",
                "description": "Generate video scripts for given topics",
                "endpoint": "/ai/generate-video-script"
            },
            {
                "name": "Scene Description",
                "description": "Generate visual descriptions for video scenes",
                "endpoint": "/ai/generate-scene-description"
            },
            {
                "name": "Image Prompt Optimization",
                "description": "Optimize prompts for image generation",
                "endpoint": "/ai/generate-image-prompt"
            },
            {
                "name": "Content Analysis",
                "description": "Analyze content for various purposes",
                "endpoint": "/ai/analyze-content"
            }
        ],
        "models": {
            "chat": "gpt-4o",
            "max_tokens": 4000,
            "temperature_range": [0.0, 1.0]
        },
        "rate_limits": {
            "requests_per_minute": 60,
            "tokens_per_minute": 150000
        }
    }
