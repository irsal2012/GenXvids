"""
User service for business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.auth import get_password_hash, verify_password
from typing import Optional


class UserService:
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = await UserService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        existing_username = await UserService.get_user_by_username(db, user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            bio=user_data.bio,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        # Update fields if provided
        if user_data.email is not None:
            # Check if email is already taken by another user
            existing_user = await UserService.get_user_by_email(db, user_data.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            user.email = user_data.email
        
        if user_data.username is not None:
            # Check if username is already taken by another user
            existing_user = await UserService.get_user_by_username(db, user_data.username)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            user.username = user_data.username
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.bio is not None:
            user.bio = user_data.bio
        
        if user_data.avatar_url is not None:
            user.avatar_url = user_data.avatar_url
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
        """Deactivate a user account"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        user.is_active = False
        await db.commit()
        
        return True
