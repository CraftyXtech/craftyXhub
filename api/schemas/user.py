from pydantic import BaseModel, EmailStr, validator, Field
from .base import TimestampMixin, BaseSchema
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=255)

class UserCreate(UserBase):
    password: str
    confirm_password: str
    
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

class UserResponse(UserBase):
    uuid: str  
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
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
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None

class ProfileBase(BaseModel):
    bio: Optional[str] = Field(None, max_length=1000)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    twitter_handle: Optional[str] = Field(None, max_length=50)
    github_handle: Optional[str] = Field(None, max_length=50)
    linkedin_handle: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[datetime] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    avatar: Optional[str] = None

class ProfileResponse(ProfileBase, TimestampMixin, BaseSchema):
    uuid: str
    avatar: Optional[str] = None


