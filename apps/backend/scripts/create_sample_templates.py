"""
Script to create sample templates for the GenXvids platform
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.database import get_db_session
from app.models.template import Template
from app.schemas.template import TemplateCategory
from datetime import datetime


async def create_sample_templates():
    """Create sample templates for different categories"""
    
    # Simple template configurations
    templates_data = [
        {
            "name": "Modern Business Intro",
            "description": "Professional business introduction template with clean animations",
            "category": TemplateCategory.BUSINESS.value,
            "tags": ["business", "professional", "intro", "corporate"],
            "duration": 15,
            "is_featured": True,
            "elements": {
                "duration": 15.0,
                "aspect_ratio": "16:9",
                "default_style": "minimalist",
                "customizable_elements": ["title_text", "subtitle_text", "logo_image"],
                "scenes": [
                    {
                        "id": "intro_scene",
                        "type": "intro",
                        "duration": 15.0,
                        "elements": [
                            {
                                "id": "title_text",
                                "type": "text",
                                "position": {"x": 50, "y": 45},
                                "size": {"width": 80, "height": 15},
                                "properties": {
                                    "text": "Your Company Name",
                                    "fontSize": 48,
                                    "fontFamily": "Montserrat",
                                    "color": "#ffffff",
                                    "textAlign": "center"
                                }
                            }
                        ]
                    }
                ]
            }
        },
        {
            "name": "Instagram Story Template",
            "description": "Trendy vertical template perfect for Instagram stories",
            "category": TemplateCategory.SOCIAL_MEDIA.value,
            "tags": ["instagram", "story", "social", "vertical"],
            "duration": 10,
            "is_featured": True,
            "elements": {
                "duration": 10.0,
                "aspect_ratio": "9:16",
                "default_style": "animated",
                "customizable_elements": ["main_text", "background_image"],
                "scenes": [
                    {
                        "id": "story_scene",
                        "type": "main",
                        "duration": 10.0,
                        "elements": [
                            {
                                "id": "main_text",
                                "type": "text",
                                "position": {"x": 50, "y": 40},
                                "size": {"width": 80, "height": 20},
                                "properties": {
                                    "text": "Your Story Here",
                                    "fontSize": 36,
                                    "fontFamily": "Poppins",
                                    "color": "#ffffff",
                                    "textAlign": "center"
                                }
                            }
                        ]
                    }
                ]
            }
        },
        {
            "name": "Product Showcase",
            "description": "Dynamic product presentation template",
            "category": TemplateCategory.MARKETING.value,
            "tags": ["product", "showcase", "marketing", "sales"],
            "duration": 20,
            "is_featured": True,
            "elements": {
                "duration": 20.0,
                "aspect_ratio": "16:9",
                "default_style": "cinematic",
                "customizable_elements": ["product_image", "product_name", "cta_text"],
                "scenes": [
                    {
                        "id": "product_scene",
                        "type": "main",
                        "duration": 20.0,
                        "elements": [
                            {
                                "id": "product_name",
                                "type": "text",
                                "position": {"x": 50, "y": 30},
                                "size": {"width": 60, "height": 12},
                                "properties": {
                                    "text": "Amazing Product",
                                    "fontSize": 38,
                                    "fontFamily": "Roboto",
                                    "color": "#ffffff",
                                    "textAlign": "center"
                                }
                            }
                        ]
                    }
                ]
            }
        }
    ]
    
    async with get_db_session() as db:
        for template_data in templates_data:
            # Check if template already exists
            existing = await db.execute(
                select(Template).where(Template.name == template_data["name"])
            )
            if existing.scalar_one_or_none():
                print(f"Template '{template_data['name']}' already exists, skipping...")
                continue
            
            # Create new template
            db_template = Template(
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                tags=template_data["tags"],
                elements=template_data["elements"],
                duration=template_data["duration"],
                is_public=True,
                is_featured=template_data["is_featured"],
                usage_count=0
            )
            
            db.add(db_template)
            print(f"Created template: {template_data['name']}")
        
        await db.commit()
        print("Sample templates created successfully!")


if __name__ == "__main__":
    asyncio.run(create_sample_templates())
