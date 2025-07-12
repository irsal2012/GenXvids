"""
Asset service for managing uploaded files
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from fastapi import HTTPException, status, UploadFile
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate, AssetSearchRequest, AssetType, AssetCategory
from typing import Optional, List, Dict, Any
import os
import uuid
from datetime import datetime
from pathlib import Path
import mimetypes
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class AssetService:
    
    @staticmethod
    async def upload_asset(
        db: AsyncSession, 
        file: UploadFile, 
        name: Optional[str] = None,
        category: Optional[AssetCategory] = None,
        tags: Optional[List[str]] = None
    ) -> Asset:
        """Upload and process an asset file"""
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No filename provided"
                )
            
            # Determine file type and validate
            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
            if not mime_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not determine file type"
                )
            
            file_type = AssetService._get_file_type(mime_type)
            if not file_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {mime_type}"
                )
            
            # Generate unique filename
            file_extension = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            
            # Set up file paths
            uploads_dir = Path(__file__).parent.parent.parent / "uploads" / "assets"
            type_dir = uploads_dir / file_type.value
            type_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = type_dir / unique_filename
            
            # Save file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Extract metadata
            metadata = await AssetService._extract_metadata(file_path, file_type, mime_type)
            
            # Create asset record
            asset_data = AssetCreate(
                name=name or Path(file.filename).stem,
                original_filename=file.filename,
                file_type=file_type,
                mime_type=mime_type,
                file_size=len(content),
                width=metadata.get("width"),
                height=metadata.get("height"),
                duration=metadata.get("duration"),
                category=category,
                tags=tags or [],
                metadata=metadata
            )
            
            db_asset = Asset(
                name=asset_data.name,
                original_filename=asset_data.original_filename,
                file_path=str(file_path),
                file_type=asset_data.file_type.value,
                mime_type=asset_data.mime_type,
                file_size=asset_data.file_size,
                width=asset_data.width,
                height=asset_data.height,
                duration=asset_data.duration,
                category=asset_data.category.value if asset_data.category else None,
                is_public=True,
                is_premium=False,
                usage_count=0
            )
            
            db.add(db_asset)
            await db.commit()
            await db.refresh(db_asset)
            
            return db_asset
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Asset upload failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload asset: {str(e)}"
            )
    
    @staticmethod
    async def get_assets(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        search_params: Optional[AssetSearchRequest] = None
    ) -> List[Asset]:
        """Get assets with optional filtering"""
        query = select(Asset).where(Asset.is_public == True)
        
        if search_params:
            if search_params.query:
                search_term = f"%{search_params.query}%"
                query = query.where(
                    or_(
                        Asset.name.ilike(search_term),
                        Asset.original_filename.ilike(search_term)
                    )
                )
            
            if search_params.file_type:
                query = query.where(Asset.file_type == search_params.file_type.value)
            
            if search_params.category:
                query = query.where(Asset.category == search_params.category.value)
            
            # Tags functionality removed - not implemented in current model
            
            if search_params.is_premium is not None:
                query = query.where(Asset.is_premium == search_params.is_premium)
            
            # Dimension filters
            if search_params.min_width:
                query = query.where(Asset.width >= search_params.min_width)
            if search_params.max_width:
                query = query.where(Asset.width <= search_params.max_width)
            if search_params.min_height:
                query = query.where(Asset.height >= search_params.min_height)
            if search_params.max_height:
                query = query.where(Asset.height <= search_params.max_height)
            
            # Duration filters
            if search_params.min_duration:
                query = query.where(Asset.duration >= search_params.min_duration)
            if search_params.max_duration:
                query = query.where(Asset.duration <= search_params.max_duration)
        
        query = query.order_by(Asset.usage_count.desc(), Asset.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_asset_by_id(db: AsyncSession, asset_id: int) -> Optional[Asset]:
        """Get asset by ID"""
        result = await db.execute(
            select(Asset).where(
                and_(Asset.id == asset_id, Asset.is_public == True)
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_asset(
        db: AsyncSession,
        asset_id: int,
        asset_data: AssetUpdate
    ) -> Optional[Asset]:
        """Update asset information"""
        asset = await AssetService.get_asset_by_id(db, asset_id)
        if not asset:
            return None
        
        update_data = asset_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "category" and value:
                setattr(asset, field, value.value)
            else:
                setattr(asset, field, value)
        
        await db.commit()
        await db.refresh(asset)
        
        return asset
    
    @staticmethod
    async def delete_asset(db: AsyncSession, asset_id: int) -> bool:
        """Delete an asset"""
        asset = await AssetService.get_asset_by_id(db, asset_id)
        if not asset:
            return False
        
        # Delete file from filesystem
        try:
            file_path = Path(asset.file_path)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete asset file: {e}")
        
        # Delete from database
        await db.delete(asset)
        await db.commit()
        
        return True
    
    @staticmethod
    async def increment_usage_count(db: AsyncSession, asset_id: int) -> bool:
        """Increment asset usage count"""
        asset = await AssetService.get_asset_by_id(db, asset_id)
        if not asset:
            return False
        
        asset.usage_count += 1
        await db.commit()
        
        return True
    
    @staticmethod
    async def get_assets_by_type(
        db: AsyncSession,
        file_type: AssetType,
        limit: int = 20
    ) -> List[Asset]:
        """Get assets by file type"""
        result = await db.execute(
            select(Asset)
            .where(
                and_(
                    Asset.file_type == file_type.value,
                    Asset.is_public == True
                )
            )
            .order_by(Asset.usage_count.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_asset_stats(db: AsyncSession) -> Dict[str, Any]:
        """Get asset statistics"""
        # Total assets
        total_result = await db.execute(
            select(func.count(Asset.id)).where(Asset.is_public == True)
        )
        total_assets = total_result.scalar()
        
        # Assets by type
        type_result = await db.execute(
            select(Asset.file_type, func.count(Asset.id))
            .where(Asset.is_public == True)
            .group_by(Asset.file_type)
        )
        by_type = {row[0]: row[1] for row in type_result.fetchall()}
        
        # Assets by category
        category_result = await db.execute(
            select(Asset.category, func.count(Asset.id))
            .where(and_(Asset.is_public == True, Asset.category.isnot(None)))
            .group_by(Asset.category)
        )
        by_category = {row[0]: row[1] for row in category_result.fetchall()}
        
        # Total size
        size_result = await db.execute(
            select(func.sum(Asset.file_size)).where(Asset.is_public == True)
        )
        total_size = size_result.scalar() or 0
        
        # Most used asset
        most_used_result = await db.execute(
            select(Asset.name, Asset.usage_count)
            .where(Asset.is_public == True)
            .order_by(Asset.usage_count.desc())
            .limit(1)
        )
        most_used = most_used_result.first()
        
        return {
            "total_assets": total_assets,
            "by_type": by_type,
            "by_category": by_category,
            "total_size": total_size,
            "most_used": {
                "name": most_used[0] if most_used else None,
                "usage_count": most_used[1] if most_used else 0
            }
        }
    
    @staticmethod
    def _get_file_type(mime_type: str) -> Optional[AssetType]:
        """Determine asset type from MIME type"""
        if mime_type.startswith("image/"):
            return AssetType.IMAGE
        elif mime_type.startswith("video/"):
            return AssetType.VIDEO
        elif mime_type.startswith("audio/"):
            return AssetType.AUDIO
        elif mime_type in ["font/ttf", "font/otf", "application/font-woff", "application/font-woff2"]:
            return AssetType.FONT
        return None
    
    @staticmethod
    async def _extract_metadata(
        file_path: Path,
        file_type: AssetType,
        mime_type: str
    ) -> Dict[str, Any]:
        """Extract metadata from uploaded file"""
        metadata = {"mime_type": mime_type}
        
        try:
            if file_type == AssetType.IMAGE:
                # Extract image metadata
                with Image.open(file_path) as img:
                    metadata.update({
                        "width": img.width,
                        "height": img.height,
                        "format": img.format,
                        "mode": img.mode
                    })
            elif file_type == AssetType.VIDEO:
                # For video files, we'd use ffprobe or similar
                # For now, just basic metadata
                metadata.update({
                    "width": None,
                    "height": None,
                    "duration": None,
                    "format": "video"
                })
            elif file_type == AssetType.AUDIO:
                # For audio files, we'd use audio libraries
                metadata.update({
                    "duration": None,
                    "format": "audio"
                })
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
        
        return metadata
