"""
Authentication Schemas for CraftyXhub API

Pydantic schemas for JWT authentication, login, token management,
and user response models following SubPRD-JWTAuthentication.md specifications.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from enum import Enum

# ---------------------------------------------------------------------------
# Shared Enumerations
# ---------------------------------------------------------------------------


class UserRole(str, Enum):
    """Enumeration of possible user roles across the application."""

    USER = "user"
    EDITOR = "editor"
    ADMIN = "admin"


# ---------------------------------------------------------------------------
# Author Response Model
# ---------------------------------------------------------------------------


class AuthorResponse(BaseModel):
    """Author information in responses"""
    id: UUID
    name: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Authentication Schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")
    remember_me: bool = Field(default=False, description="Extended session duration")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "remember_me": False
            }
        }
    }


class TokenResponse(BaseModel):
    """Response schema for JWT tokens."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...", 
                "token_type": "bearer",
                "expires_in": 900
            }
        }
    }


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""
    refresh_token: str = Field(..., description="Valid refresh token")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


class UserResponse(BaseModel):
    """Response schema for user information."""
    id: UUID = Field(..., description="User unique identifier")
    name: str = Field(..., description="User full name")
    email: EmailStr = Field(..., description="User email address")
    role: str = Field(..., description="User role (user, editor, admin)")
    avatar: Optional[str] = Field(None, description="User avatar URL")
    bio: Optional[str] = Field(None, description="User biography")
    email_verified_at: Optional[datetime] = Field(None, description="Email verification timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "John Doe",
                "email": "john@example.com",
                "role": "user",
                "avatar": "/media/avatars/john.jpg",
                "bio": "Content creator and tech enthusiast",
                "email_verified_at": "2024-01-15T10:30:00Z",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    }


class LoginResponse(BaseModel):
    """Complete login response with tokens and user data."""
    user: UserResponse = Field(..., description="User information")
    tokens: TokenResponse = Field(..., description="Authentication tokens")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "user",
                    "avatar": None,
                    "bio": None,
                    "email_verified_at": "2024-01-15T10:30:00Z",
                    "created_at": "2024-01-01T00:00:00Z"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 900
                }
            }
        }
    }


class LogoutRequest(BaseModel):
    """Request schema for user logout."""
    revoke_all_tokens: bool = Field(default=False, description="Revoke all user tokens")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "revoke_all_tokens": False
            }
        }
    }


class AuthError(BaseModel):
    """Error response schema for authentication failures."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "invalid_credentials",
                "message": "Invalid email or password",
                "details": None
            }
        }
    }


class TokenClaims(BaseModel):
    """JWT token claims structure."""
    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")
    iss: str = Field(default="craftyhub", description="Token issuer")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "sub": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "role": "user",
                "exp": 1640995200,
                "iat": 1640991600,
                "iss": "craftyhub"
            }
        }
    } 