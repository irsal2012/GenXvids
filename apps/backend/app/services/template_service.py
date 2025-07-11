"""
Template service for business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from fastapi import HTTPException, status
from app.models.template import Template
from app.schemas.template import (
    TemplateCreate, 
    TemplateUpdate, 
    TemplateSearchRequest,
    TemplateCategory
)
from typing import Optional, List, Dict, Any
import json
from datetime import datetime


class TemplateService:
    
    @staticmethod
    async def create_template(db: AsyncSession, template_data: TemplateCreate) -> Template:
        """Create a new template"""
        try:
            # Convert TemplateConfig to dict for JSON storage
            elements_dict = template_data.elements.model_dump()
            
            # Create template record
            db_template = Template(
                name=template_data.name,
                description=template_data.description,
                category=template_data.category.value,
                tags=template_data.tags,
                elements=elements_dict,
                settings=template_data.settings,
                duration=int(template_data.elements.duration),
                is_public=template_data.is_public,
                is_featured=template_data.is_featured,
                usage_count=0
            )
            
            db.add(db_template)
            await db.commit()
            await db.refresh(db_template)
            
            return db_template
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create template: {str(e)}"
            )
    
    @staticmethod
    async def get_templates(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 20,
        search_params: Optional[TemplateSearchRequest] = None
    ) -> List[Template]:
        """Get templates with optional filtering"""
        query = select(Template).where(Template.is_public == True)
        
        # Apply search filters
        if search_params:
            if search_params.query:
                search_term = f"%{search_params.query}%"
                query = query.where(
                    or_(
                        Template.name.ilike(search_term),
                        Template.description.ilike(search_term)
                    )
                )
            
            if search_params.category:
                query = query.where(Template.category == search_params.category.value)
            
            if search_params.tags:
                # Filter by tags (PostgreSQL JSON contains)
                for tag in search_params.tags:
                    query = query.where(Template.tags.contains([tag]))
            
            if search_params.is_featured is not None:
                query = query.where(Template.is_featured == search_params.is_featured)
            
            if search_params.duration_min:
                query = query.where(Template.duration >= search_params.duration_min)
            
            if search_params.duration_max:
                query = query.where(Template.duration <= search_params.duration_max)
        
        # Order by featured first, then by usage count, then by creation date
        query = query.order_by(
            Template.is_featured.desc(),
            Template.usage_count.desc(),
            Template.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_template_by_id(db: AsyncSession, template_id: int) -> Optional[Template]:
        """Get template by ID"""
        result = await db.execute(
            select(Template).where(
                and_(
                    Template.id == template_id,
                    Template.is_public == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_featured_templates(db: AsyncSession, limit: int = 10) -> List[Template]:
        """Get featured templates"""
        result = await db.execute(
            select(Template)
            .where(
                and_(
                    Template.is_featured == True,
                    Template.is_public == True
                )
            )
            .order_by(Template.usage_count.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_templates_by_category(
        db: AsyncSession, 
        category: TemplateCategory, 
        limit: int = 20
    ) -> List[Template]:
        """Get templates by category"""
        result = await db.execute(
            select(Template)
            .where(
                and_(
                    Template.category == category.value,
                    Template.is_public == True
                )
            )
            .order_by(Template.usage_count.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def update_template(
        db: AsyncSession, 
        template_id: int, 
        template_data: TemplateUpdate
    ) -> Optional[Template]:
        """Update template information"""
        template = await TemplateService.get_template_by_id(db, template_id)
        if not template:
            return None
        
        # Update fields if provided
        update_data = template_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "elements" and value:
                # Convert TemplateConfig to dict for JSON storage
                setattr(template, field, value.model_dump())
                # Update duration from elements
                template.duration = int(value.duration)
            elif field == "category" and value:
                setattr(template, field, value.value)
            else:
                setattr(template, field, value)
        
        await db.commit()
        await db.refresh(template)
        
        return template
    
    @staticmethod
    async def delete_template(db: AsyncSession, template_id: int) -> bool:
        """Delete a template (admin only - mark as not public)"""
        template = await TemplateService.get_template_by_id(db, template_id)
        if not template:
            return False
        
        # Instead of deleting, mark as not public
        template.is_public = False
        await db.commit()
        
        return True
    
    @staticmethod
    async def increment_usage_count(db: AsyncSession, template_id: int) -> bool:
        """Increment template usage count"""
        template = await TemplateService.get_template_by_id(db, template_id)
        if not template:
            return False
        
        template.usage_count += 1
        await db.commit()
        
        return True
    
    @staticmethod
    async def get_popular_templates(db: AsyncSession, limit: int = 10) -> List[Template]:
        """Get most popular templates"""
        result = await db.execute(
            select(Template)
            .where(Template.is_public == True)
            .order_by(Template.usage_count.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def search_templates_by_tags(
        db: AsyncSession, 
        tags: List[str], 
        limit: int = 20
    ) -> List[Template]:
        """Search templates by tags"""
        query = select(Template).where(Template.is_public == True)
        
        # Filter by all provided tags
        for tag in tags:
            query = query.where(Template.tags.contains([tag]))
        
        query = query.order_by(Template.usage_count.desc()).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_template_stats(db: AsyncSession) -> Dict[str, Any]:
        """Get template statistics"""
        # Total templates
        total_result = await db.execute(
            select(func.count(Template.id)).where(Template.is_public == True)
        )
        total_templates = total_result.scalar()
        
        # Templates by category
        category_result = await db.execute(
            select(Template.category, func.count(Template.id))
            .where(Template.is_public == True)
            .group_by(Template.category)
        )
        categories = {row[0]: row[1] for row in category_result.fetchall()}
        
        # Featured templates count
        featured_result = await db.execute(
            select(func.count(Template.id))
            .where(
                and_(
                    Template.is_featured == True,
                    Template.is_public == True
                )
            )
        )
        featured_count = featured_result.scalar()
        
        # Most used template
        most_used_result = await db.execute(
            select(Template.name, Template.usage_count)
            .where(Template.is_public == True)
            .order_by(Template.usage_count.desc())
            .limit(1)
        )
        most_used = most_used_result.first()
        
        return {
            "total_templates": total_templates,
            "featured_templates": featured_count,
            "categories": categories,
            "most_used_template": {
                "name": most_used[0] if most_used else None,
                "usage_count": most_used[1] if most_used else 0
            }
        }
    
    @staticmethod
    async def validate_template_config(template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template configuration"""
        errors = []
        warnings = []
        
        try:
            # Check required fields
            required_fields = ["duration", "aspect_ratio", "scenes", "default_style"]
            for field in required_fields:
                if field not in template_config:
                    errors.append(f"Missing required field: {field}")
            
            # Validate scenes
            if "scenes" in template_config:
                scenes = template_config["scenes"]
                if not isinstance(scenes, list) or len(scenes) == 0:
                    errors.append("Template must have at least one scene")
                else:
                    total_duration = 0
                    for i, scene in enumerate(scenes):
                        if not isinstance(scene, dict):
                            errors.append(f"Scene {i} must be an object")
                            continue
                        
                        # Check scene required fields
                        scene_required = ["id", "type", "duration", "elements"]
                        for field in scene_required:
                            if field not in scene:
                                errors.append(f"Scene {i} missing required field: {field}")
                        
                        if "duration" in scene:
                            total_duration += scene["duration"]
                        
                        # Validate elements
                        if "elements" in scene:
                            elements = scene["elements"]
                            if not isinstance(elements, list) or len(elements) == 0:
                                errors.append(f"Scene {i} must have at least one element")
                            else:
                                for j, element in enumerate(elements):
                                    if not isinstance(element, dict):
                                        errors.append(f"Scene {i}, element {j} must be an object")
                                        continue
                                    
                                    # Check element required fields
                                    element_required = ["id", "type", "position", "size"]
                                    for field in element_required:
                                        if field not in element:
                                            errors.append(f"Scene {i}, element {j} missing required field: {field}")
            
            # Check if total scene duration matches template duration
            if "duration" in template_config and total_duration > 0:
                template_duration = template_config["duration"]
                if abs(total_duration - template_duration) > 0.1:  # Allow small floating point differences
                    warnings.append(f"Total scene duration ({total_duration}s) doesn't match template duration ({template_duration}s)")
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
