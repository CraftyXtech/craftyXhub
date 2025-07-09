"""
User Registration Schemas for CraftyXhub API

Pydantic schemas for user registration, email verification, and onboarding
following SubPRD-UserRegistration.md specifications.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID
from .auth import UserResponse, RefreshTokenResponse


class UserRegistration(BaseModel):
    """Request schema for user registration."""
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    confirm_password: str = Field(..., description="Password confirmation")
    terms_accepted: bool = Field(..., description="Terms of service acceptance (must be True)")
    newsletter_enabled: bool = Field(default=True, description="Newsletter subscription preference")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('terms_accepted')
    def terms_must_be_accepted(cls, v):
        """Validate that terms of service are accepted."""
        if not v:
            raise ValueError('Terms of service must be accepted')
        return v
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one number, and one special character'
            )
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "terms_accepted": True,
                "newsletter_enabled": True
            }
        }
    }


class RegistrationResponse(BaseModel):
    """Response schema for successful registration."""
    user: UserResponse = Field(..., description="Created user information")
    tokens: Optional[RefreshTokenResponse] = Field(None, description="Authentication tokens (if email verified)")
    email_verification_required: bool = Field(..., description="Whether email verification is required")
    message: str = Field(..., description="Success message")
    
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
                    "email_verified_at": None,
                    "created_at": "2024-01-01T00:00:00Z"
                },
                "tokens": None,
                "email_verification_required": True,
                "message": "Registration successful. Please check your email to verify your account."
            }
        }
    }


class EmailVerificationRequest(BaseModel):
    """Request schema for email verification."""
    token: str = Field(..., min_length=32, description="Email verification token")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "token": "abc123def456ghi789jkl012mno345pqr678stu901"
            }
        }
    }


class EmailVerificationResponse(BaseModel):
    """Response schema for email verification."""
    user: UserResponse = Field(..., description="Verified user information")
    tokens: RefreshTokenResponse = Field(..., description="Authentication tokens")
    message: str = Field(..., description="Success message")
    
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
                    "email_verified_at": "2024-01-01T12:00:00Z",
                    "created_at": "2024-01-01T00:00:00Z"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 900
                },
                "message": "Email verified successfully. You are now logged in."
            }
        }
    }


class ResendVerificationRequest(BaseModel):
    """Request schema for resending verification email."""
    email: EmailStr = Field(..., description="User email address")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john@example.com"
            }
        }
    }


class ResendVerificationResponse(BaseModel):
    """Response schema for resending verification email."""
    message: str = Field(..., description="Success message")
    email: EmailStr = Field(..., description="Email address where verification was sent")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Verification email sent successfully.",
                "email": "john@example.com"
            }
        }
    }


class OnboardingPreferences(BaseModel):
    """Schema for user onboarding preferences."""
    interested_categories: list[str] = Field(default=[], description="List of category slugs user is interested in")
    followed_topics: list[str] = Field(default=[], description="List of tag slugs user wants to follow")
    newsletter_frequency: str = Field(default="weekly", description="Newsletter frequency preference")
    notification_preferences: dict = Field(default={}, description="Notification preference settings")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "interested_categories": ["web-development", "python", "javascript"],
                "followed_topics": ["fastapi", "react", "machine-learning"],
                "newsletter_frequency": "weekly",
                "notification_preferences": {
                    "email_comments": True,
                    "email_likes": False,
                    "email_follows": True
                }
            }
        }
    }


class OnboardingResponse(BaseModel):
    """Response schema for completed onboarding."""
    message: str = Field(..., description="Success message")
    user: UserResponse = Field(..., description="Updated user information")
    preferences_saved: bool = Field(..., description="Whether preferences were saved successfully")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Onboarding completed successfully.",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "user",
                    "avatar": None,
                    "bio": None,
                    "email_verified_at": "2024-01-01T12:00:00Z",
                    "created_at": "2024-01-01T00:00:00Z"
                },
                "preferences_saved": True
            }
        }
    } 