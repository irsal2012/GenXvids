"""
OpenAI service for handling AI-powered features
"""

import asyncio
from typing import Optional, List, Dict, Any
from openai import AsyncAzureOpenAI
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with Azure OpenAI API"""
    
    def __init__(self):
        """Initialize the OpenAI service"""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Azure OpenAI client"""
        try:
            if not all([
                settings.AZURE_OPENAI_API_KEY,
                settings.AZURE_OPENAI_ENDPOINT,
                settings.AZURE_OPENAI_DEPLOYMENT
            ]):
                logger.warning("Azure OpenAI configuration incomplete. Service will be disabled.")
                return
            
            self.client = AsyncAzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                timeout=settings.AZURE_OPENAI_TIMEOUT,
                max_retries=settings.AZURE_OPENAI_MAX_RETRIES
            )
            logger.info("Azure OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            self.client = None
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate text using Azure OpenAI
        
        Args:
            prompt: The user prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_message: Optional system message
            
        Returns:
            Generated text or None if failed
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None
        
        try:
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT,
                messages=messages,
                max_tokens=max_tokens or settings.AZURE_OPENAI_MAX_TOKENS,
                temperature=temperature or settings.AZURE_OPENAI_TEMPERATURE
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return None
    
    async def generate_video_script(
        self,
        topic: str,
        duration: int = 60,
        style: str = "engaging"
    ) -> Optional[str]:
        """
        Generate a video script for the given topic
        
        Args:
            topic: The video topic
            duration: Target duration in seconds
            style: Script style (engaging, professional, casual, etc.)
            
        Returns:
            Generated script or None if failed
        """
        system_message = f"""You are a professional video script writer. Create engaging, well-structured video scripts that are appropriate for the target duration and style.

Guidelines:
- Keep scripts concise and engaging
- Include natural transitions
- Consider pacing for video content
- Make content accessible and interesting
- Target duration: {duration} seconds
- Style: {style}"""

        prompt = f"""Create a video script about: {topic}

The script should be approximately {duration} seconds long when spoken at a normal pace (roughly {duration // 60} minutes).

Please structure the script with:
1. Hook/Opening (grab attention)
2. Main content (key points)
3. Conclusion/Call to action

Make it {style} in tone and suitable for video content."""

        return await self.generate_text(
            prompt=prompt,
            system_message=system_message,
            max_tokens=settings.AI_SCRIPT_MAX_LENGTH
        )
    
    async def generate_scene_description(
        self,
        script_segment: str,
        visual_style: str = "modern"
    ) -> Optional[str]:
        """
        Generate visual scene descriptions for video segments
        
        Args:
            script_segment: The script text to create visuals for
            visual_style: Visual style preference
            
        Returns:
            Scene description or None if failed
        """
        system_message = f"""You are a video director creating visual descriptions for video scenes. Generate detailed but concise visual descriptions that complement the script content.

Guidelines:
- Describe visual elements, camera angles, and scene composition
- Keep descriptions practical for video production
- Consider the visual style: {visual_style}
- Focus on enhancing the script's message
- Be specific but not overly complex"""

        prompt = f"""Create a visual scene description for this script segment:

"{script_segment}"

Visual style: {visual_style}

Describe:
- Scene setting and environment
- Visual elements and composition
- Camera angles or movements (if relevant)
- Any graphics, text overlays, or visual effects
- Color scheme or mood

Keep the description concise but detailed enough for video production."""

        return await self.generate_text(
            prompt=prompt,
            system_message=system_message,
            max_tokens=settings.AI_SCENE_DESCRIPTION_MAX_LENGTH
        )
    
    async def generate_image_prompt(
        self,
        description: str,
        style: str = "photorealistic"
    ) -> Optional[str]:
        """
        Generate optimized prompts for image generation
        
        Args:
            description: Basic description of desired image
            style: Image style preference
            
        Returns:
            Optimized image prompt or None if failed
        """
        system_message = """You are an expert at creating prompts for AI image generation. Transform basic descriptions into detailed, effective prompts that will produce high-quality images.

Guidelines:
- Include specific details about composition, lighting, and style
- Use descriptive adjectives and technical terms
- Consider aspect ratio and quality modifiers
- Make prompts clear and specific
- Optimize for the requested style"""

        prompt = f"""Transform this basic image description into an optimized prompt for AI image generation:

Description: {description}
Style: {style}

Create a detailed prompt that includes:
- Specific visual details
- Composition and framing
- Lighting and mood
- Style and quality modifiers
- Technical specifications if relevant

Return only the optimized prompt, no additional text."""

        return await self.generate_text(
            prompt=prompt,
            system_message=system_message,
            max_tokens=200
        )
    
    async def analyze_content(
        self,
        content: str,
        analysis_type: str = "general"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze content for various purposes
        
        Args:
            content: Content to analyze
            analysis_type: Type of analysis (sentiment, topics, quality, etc.)
            
        Returns:
            Analysis results or None if failed
        """
        if not settings.AI_ENABLE_CONTENT_FILTERING:
            return {"status": "disabled", "message": "Content filtering is disabled"}
        
        system_message = f"""You are a content analyst. Analyze the provided content and return structured insights.

Analysis type: {analysis_type}

Return your analysis in a structured format that includes relevant metrics and insights."""

        prompt = f"""Analyze this content:

"{content}"

Provide analysis for: {analysis_type}

Return a structured analysis with relevant insights, scores, and recommendations."""

        try:
            result = await self.generate_text(
                prompt=prompt,
                system_message=system_message,
                max_tokens=500
            )
            
            if result:
                return {
                    "analysis_type": analysis_type,
                    "content_length": len(content),
                    "result": result,
                    "status": "success"
                }
            else:
                return {"status": "failed", "message": "Analysis failed"}
                
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return {"status": "error", "message": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the OpenAI service
        
        Returns:
            Health status information
        """
        if not self.client:
            return {
                "status": "unhealthy",
                "message": "OpenAI client not initialized",
                "configured": False
            }
        
        try:
            # Simple test request
            test_response = await self.generate_text(
                prompt="Say 'Hello' if you can hear me.",
                max_tokens=10
            )
            
            return {
                "status": "healthy" if test_response else "unhealthy",
                "configured": True,
                "endpoint": settings.AZURE_OPENAI_ENDPOINT,
                "deployment": settings.AZURE_OPENAI_DEPLOYMENT,
                "api_version": settings.AZURE_OPENAI_API_VERSION,
                "test_successful": bool(test_response)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "configured": True,
                "error": str(e),
                "message": "Failed to connect to OpenAI service"
            }


# Create global instance
openai_service = OpenAIService()
