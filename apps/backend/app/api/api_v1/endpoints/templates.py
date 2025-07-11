"""
Template endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.template import (
    TemplateCreate, 
    TemplateUpdate, 
    TemplateResponse,
    TemplateDetailResponse,
    TemplateSearchRequest,
    TemplateCategory
)
from app.services.template_service import TemplateService
from app.utils.template_customizer import TemplateCustomizer
from typing import List, Optional

router = APIRouter()


@router.get("/", response_model=dict)
async def get_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[TemplateCategory] = None,
    featured: Optional[bool] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    search: Optional[str] = None,
    duration_min: Optional[int] = Query(None, ge=1),
    duration_max: Optional[int] = Query(None, ge=1),
    db: AsyncSession = Depends(get_db)
):
    """Get templates with filtering options"""
    try:
        # Parse tags if provided
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Create search parameters
        search_params = TemplateSearchRequest(
            query=search,
            category=category,
            tags=tag_list if tag_list else None,
            is_featured=featured,
            duration_min=duration_min,
            duration_max=duration_max
        )
        
        templates = await TemplateService.get_templates(db, skip, limit, search_params)
        
        template_data = []
        for template in templates:
            template_data.append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "tags": template.tags or [],
                "thumbnail_path": template.thumbnail_path,
                "preview_video_path": template.preview_video_path,
                "duration": template.duration,
                "is_public": template.is_public,
                "is_featured": template.is_featured,
                "usage_count": template.usage_count,
                "created_at": template.created_at.isoformat(),
                "updated_at": template.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "message": "Templates retrieved successfully",
            "data": template_data,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": len(template_data)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve templates: {str(e)}"
        )


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new template"""
    try:
        # Validate template configuration
        validation_result = await TemplateService.validate_template_config(
            template_data.elements.model_dump()
        )
        
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Template configuration is invalid",
                    "errors": validation_result["errors"],
                    "warnings": validation_result.get("warnings", [])
                }
            )
        
        template = await TemplateService.create_template(db, template_data)
        
        return {
            "success": True,
            "message": "Template created successfully",
            "data": {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "tags": template.tags or [],
                "duration": template.duration,
                "is_public": template.is_public,
                "is_featured": template.is_featured,
                "created_at": template.created_at.isoformat()
            },
            "validation": {
                "warnings": validation_result.get("warnings", [])
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Template creation failed: {str(e)}"
        )


@router.get("/featured", response_model=dict)
async def get_featured_templates(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get featured templates"""
    try:
        templates = await TemplateService.get_featured_templates(db, limit)
        
        template_data = []
        for template in templates:
            template_data.append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "tags": template.tags or [],
                "thumbnail_path": template.thumbnail_path,
                "preview_video_path": template.preview_video_path,
                "duration": template.duration,
                "usage_count": template.usage_count,
                "created_at": template.created_at.isoformat()
            })
        
        return {
            "success": True,
            "message": "Featured templates retrieved successfully",
            "data": template_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve featured templates: {str(e)}"
        )


@router.get("/popular", response_model=dict)
async def get_popular_templates(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get most popular templates"""
    try:
        templates = await TemplateService.get_popular_templates(db, limit)
        
        template_data = []
        for template in templates:
            template_data.append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "tags": template.tags or [],
                "thumbnail_path": template.thumbnail_path,
                "preview_video_path": template.preview_video_path,
                "duration": template.duration,
                "usage_count": template.usage_count,
                "created_at": template.created_at.isoformat()
            })
        
        return {
            "success": True,
            "message": "Popular templates retrieved successfully",
            "data": template_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve popular templates: {str(e)}"
        )


@router.get("/categories/{category}", response_model=dict)
async def get_templates_by_category(
    category: TemplateCategory,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get templates by category"""
    try:
        templates = await TemplateService.get_templates_by_category(db, category, limit)
        
        template_data = []
        for template in templates:
            template_data.append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "tags": template.tags or [],
                "thumbnail_path": template.thumbnail_path,
                "preview_video_path": template.preview_video_path,
                "duration": template.duration,
                "usage_count": template.usage_count,
                "created_at": template.created_at.isoformat()
            })
        
        return {
            "success": True,
            "message": f"Templates in {category.value} category retrieved successfully",
            "data": template_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve templates by category: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_template_stats(db: AsyncSession = Depends(get_db)):
    """Get template statistics"""
    try:
        stats = await TemplateService.get_template_stats(db)
        
        return {
            "success": True,
            "message": "Template statistics retrieved successfully",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve template statistics: {str(e)}"
        )


@router.get("/{template_id}", response_model=dict)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get template by ID with full configuration"""
    try:
        template = await TemplateService.get_template_by_id(db, template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return {
            "success": True,
            "message": "Template retrieved successfully",
            "data": {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "tags": template.tags or [],
                "thumbnail_path": template.thumbnail_path,
                "preview_video_path": template.preview_video_path,
                "duration": template.duration,
                "elements": template.elements,
                "settings": template.settings,
                "is_public": template.is_public,
                "is_featured": template.is_featured,
                "usage_count": template.usage_count,
                "created_at": template.created_at.isoformat(),
                "updated_at": template.updated_at.isoformat()
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve template: {str(e)}"
        )


@router.put("/{template_id}", response_model=dict)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update template information"""
    try:
        # Validate template configuration if elements are being updated
        if template_data.elements:
            validation_result = await TemplateService.validate_template_config(
                template_data.elements.model_dump()
            )
            
            if not validation_result["is_valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Template configuration is invalid",
                        "errors": validation_result["errors"],
                        "warnings": validation_result.get("warnings", [])
                    }
                )
        
        template = await TemplateService.update_template(db, template_id, template_data)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return {
            "success": True,
            "message": "Template updated successfully",
            "data": {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "tags": template.tags or [],
                "duration": template.duration,
                "is_public": template.is_public,
                "is_featured": template.is_featured,
                "updated_at": template.updated_at.isoformat()
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}"
        )


@router.delete("/{template_id}", response_model=dict)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete template (mark as not public)"""
    try:
        success = await TemplateService.delete_template(db, template_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return {
            "success": True,
            "message": "Template deleted successfully",
            "data": None
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete template: {str(e)}"
        )


@router.post("/{template_id}/use", response_model=dict)
async def use_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark template as used (increment usage count)"""
    try:
        success = await TemplateService.increment_usage_count(db, template_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return {
            "success": True,
            "message": "Template usage recorded successfully",
            "data": None
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record template usage: {str(e)}"
        )


@router.post("/{template_id}/validate", response_model=dict)
async def validate_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Validate template configuration"""
    try:
        template = await TemplateService.get_template_by_id(db, template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        validation_result = await TemplateService.validate_template_config(template.elements)
        
        return {
            "success": True,
            "message": "Template validation completed",
            "data": validation_result
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate template: {str(e)}"
        )


@router.get("/{template_id}/customizable", response_model=dict)
async def get_customizable_elements(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get customizable elements for a template"""
    try:
        template = await TemplateService.get_template_by_id(db, template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        customizable_elements = TemplateCustomizer.get_customizable_elements(template.elements)
        
        return {
            "success": True,
            "message": "Customizable elements retrieved successfully",
            "data": {
                "template_id": template_id,
                "customizable_elements": customizable_elements,
                "total_customizable": len(customizable_elements)
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get customizable elements: {str(e)}"
        )


@router.post("/{template_id}/customize", response_model=dict)
async def customize_template(
    template_id: int,
    customizations: dict,
    db: AsyncSession = Depends(get_db)
):
    """Apply customizations to a template and return the customized configuration"""
    try:
        template = await TemplateService.get_template_by_id(db, template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Validate customizations
        validation_result = TemplateCustomizer.validate_customizations(
            template.elements, customizations
        )
        
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Invalid customizations",
                    "errors": validation_result["errors"],
                    "warnings": validation_result.get("warnings", [])
                }
            )
        
        # Apply customizations
        customized_config = TemplateCustomizer.customize_template(
            template.elements, customizations
        )
        
        return {
            "success": True,
            "message": "Template customized successfully",
            "data": {
                "template_id": template_id,
                "original_config": template.elements,
                "customizations": customizations,
                "customized_config": customized_config
            },
            "validation": {
                "warnings": validation_result.get("warnings", [])
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to customize template: {str(e)}"
        )


@router.post("/{template_id}/preview", response_model=dict)
async def generate_template_preview(
    template_id: int,
    customizations: Optional[dict] = None,
    db: AsyncSession = Depends(get_db)
):
    """Generate a preview configuration for a template with optional customizations"""
    try:
        template = await TemplateService.get_template_by_id(db, template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Generate preview configuration
        if customizations:
            # Validate customizations first
            validation_result = TemplateCustomizer.validate_customizations(
                template.elements, customizations
            )
            
            if not validation_result["is_valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Invalid customizations for preview",
                        "errors": validation_result["errors"]
                    }
                )
            
            preview_config = TemplateCustomizer.generate_preview_config(
                template.elements, customizations
            )
        else:
            preview_config = TemplateCustomizer.generate_preview_config(
                template.elements, {}
            )
        
        return {
            "success": True,
            "message": "Preview configuration generated successfully",
            "data": {
                "template_id": template_id,
                "preview_config": preview_config,
                "customizations_applied": customizations is not None
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
        )


@router.post("/{template_id}/validate-customizations", response_model=dict)
async def validate_template_customizations(
    template_id: int,
    customizations: dict,
    db: AsyncSession = Depends(get_db)
):
    """Validate customizations against a template without applying them"""
    try:
        template = await TemplateService.get_template_by_id(db, template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Validate customizations
        validation_result = TemplateCustomizer.validate_customizations(
            template.elements, customizations
        )
        
        return {
            "success": True,
            "message": "Customization validation completed",
            "data": {
                "template_id": template_id,
                "validation_result": validation_result,
                "customizations": customizations
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate customizations: {str(e)}"
        )
