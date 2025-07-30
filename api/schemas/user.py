from pydantic import BaseModel, EmailStr, validator, Field, EmailStr, computed_field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID
from .base import TimestampMixin, BaseSchema

class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    full_name: str = Field(..., min_length=1, max_length=255)

class UserCreate(UserBase):
    password: str
    confirm_password: str
    role: Optional[UserRole] = UserRole.USER
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    uuid: str
    username: str
    full_name: str
    email: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def is_following(self) -> bool:
        return False

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str
    
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    role: Optional[UserRole] = None

class ProfileBase(BaseModel):
    avatar: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    twitter_handle: Optional[str] = Field(None, max_length=50)
    github_handle: Optional[str] = Field(None, max_length=50)
    linkedin_handle: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[datetime] = None
    follower_notifications: Optional[bool] = True

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    avatar: Optional[str] = None

class ProfileResponse(ProfileBase, TimestampMixin, BaseSchema):
    uuid: str

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class UserWithProfileResponse(UserResponse):
    profile: Optional[ProfileResponse] = None

class FollowResponse(BaseModel):
    user: UserResponse
    followed_at: datetime


class FollowActionResponse(BaseModel):
    success: bool
    message: str
    is_following: bool
    follower_count: int
    
class UserFollowersResponse(BaseModel):
    followers: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

class UserFollowingResponse(BaseModel):
    following: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
    
class MediaResponse(BaseModel):
    uuid: UUID
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    mime_type: str
    description: Optional[str]
    
class MediaUpdateRequest(BaseModel):
    description: Optional[str]