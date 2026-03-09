from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationInfo,
    computed_field,
    field_validator,
)
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID
from .base import TimestampMixin, BaseSchema


def _validate_password_strength(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters long")
    return value

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
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
    
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get("password") and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    uuid: str
    email: EmailStr
    username: str
    full_name: str
    is_active: bool
    is_verified: bool
    role: UserRole
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @computed_field
    @property
    def is_following(self) -> bool:
        return False

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None

class AuthResult(BaseModel):
    user: UserResponse
    token: Token

class ResetPasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)

    @field_validator("confirm_new_password")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get("new_password") and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class PasswordResetRequestEmail(BaseModel):
    """Request password reset via email (public endpoint)"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token (public endpoint)"""
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)
    
    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get("new_password") and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class AdminPasswordResetRequest(BaseModel):
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get("new_password") and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class EmailVerificationRequest(BaseModel):
    """Verify email with token"""
    token: str


class PasswordResetResponse(BaseModel):
    """Response for password reset operations"""
    message: str
    success: bool = True
    debug_reset_token: Optional[str] = None
    debug_reset_url: Optional[str] = None
    
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
    twitter_handle: Optional[str] = Field(None, max_length=100)
    linkedin_handle: Optional[str] = Field(None, max_length=100)
    instagram_handle: Optional[str] = Field(None, max_length=100)
    facebook_handle: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[datetime] = None
    follower_notifications: Optional[bool] = True


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    avatar: Optional[str] = None


class ProfileResponse(ProfileBase, TimestampMixin, BaseSchema):
    uuid: str


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


class UserSuggestionsResponse(BaseModel):
    """Response for user suggestions endpoint"""
    users: List[UserResponse]
    total: int
    
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


class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_verified: Optional[bool] = None


class UserRoleUpdate(BaseModel):
    role: UserRole
    reason: Optional[str] = None


class UserStatusUpdate(BaseModel):
    is_active: bool


class AdminUserResponse(UserWithProfileResponse):
    model_config = ConfigDict(from_attributes=True)


class AdminUserListResponse(BaseModel):
    users: List[AdminUserResponse]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool


class AdminUserStatsResponse(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    admin_count: int
    moderator_count: int
    user_count: int
    recent_registrations: int


class UserRoleChangeResponse(BaseModel):
    uuid: str
    old_role: UserRole
    new_role: UserRole
    reason: Optional[str] = None
    created_at: datetime
    changed_by: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class UserRoleChangeListResponse(BaseModel):
    changes: List[UserRoleChangeResponse]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool


class AdminUserDeletionResponse(BaseModel):
    message: str
    deleted_user_uuid: str
    deleted_counts: dict[str, int]
    failed_file_cleanup: List[str] = Field(default_factory=list)
