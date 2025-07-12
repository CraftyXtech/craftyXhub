
from typing import Union, Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from enum import Enum
from uuid import UUID

# User role enumeration - following FastAPI best practices
class UserRole(str, Enum):
    """User role enumeration for role-based access control."""
    USER = "user"
    EDITOR = "editor"
    ADMIN = "admin"

# Token schemas - exactly as in FastAPI tutorial
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

# User schemas - following FastAPI tutorial pattern
class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str

# Login request schema - for OAuth2PasswordRequestForm compatibility
class UserLogin(BaseModel):
    username: str
    password: str

# Additional schemas for our specific needs
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserResponse(BaseModel):
    id: UUID  # Changed from int to UUID
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

# Legacy schemas for backward compatibility
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class LogoutRequest(BaseModel):
    token: str

class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    expires_at: Optional[datetime] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class EmailVerificationRequest(BaseModel):
    token: str

class TwoFactorSetupResponse(BaseModel):
    qr_code: str
    secret: str
    backup_codes: List[str]

class TwoFactorVerifyRequest(BaseModel):
    token: str
    code: str

class TwoFactorLoginRequest(BaseModel):
    email: EmailStr
    password: str
    two_factor_code: str
    remember_me: bool = False

# Validation schemas
class PasswordStrengthResponse(BaseModel):
    is_strong: bool
    score: int
    feedback: List[str]
    requirements_met: dict

# OAuth schemas
class OAuthLoginRequest(BaseModel):
    provider: str
    code: str
    state: Optional[str] = None
    redirect_uri: Optional[str] = None

class OAuthLinkRequest(BaseModel):
    provider: str
    code: str
    state: Optional[str] = None

# API Key schemas
class APIKeyCreate(BaseModel):
    name: str
    expires_at: Optional[datetime] = None
    permissions: List[str] = []

class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: str  # Only returned on creation
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    permissions: List[str] = []

class APIKeyList(BaseModel):
    id: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    permissions: List[str] = [] 