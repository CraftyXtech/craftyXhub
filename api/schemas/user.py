

from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr
from schemas.auth import UserRole


class UserSummaryResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    avatar: Optional[str] = None
    role: UserRole
    is_active: bool = True

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    avatar: Optional[str] = None
    role: UserRole
    is_active: bool = True
    is_verified: bool = False
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    twitter_handle: Optional[str] = None
    github_handle: Optional[str] = None
    linkedin_handle: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    avatar: Optional[str] = None
    role: UserRole
    is_active: bool = True
    is_verified: bool = False
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    twitter_handle: Optional[str] = None
    github_handle: Optional[str] = None
    linkedin_handle: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    # Statistics
    posts_count: int = 0
    comments_count: int = 0
    likes_received: int = 0
    followers_count: int = 0
    following_count: int = 0

    class Config:
        from_attributes = True 