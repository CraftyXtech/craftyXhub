
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from .user import UserResponse


class UserRegistration(BaseModel):
    """Request schema for user registration with validation."""
    
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        description="User full name",
        example="John Doe"
    )
    email: EmailStr = Field(
        ..., 
        description="User email address",
        example="john.doe@example.com"
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128,
        description="User password (min 8 characters with mixed case, number, and special character)",
        example="SecurePass123!"
    )
    confirm_password: str = Field(
        ..., 
        description="Password confirmation",
        example="SecurePass123!"
    )
    terms_accepted: bool = Field(
        ..., 
        description="Terms of service acceptance (must be True)",
        example=True
    )
    newsletter_enabled: bool = Field(
        default=True, 
        description="Newsletter subscription preference",
        example=True
    )
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        """Validate that passwords match."""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @field_validator('terms_accepted')
    @classmethod
    def terms_must_be_accepted(cls, v):
        """Validate that terms of service are accepted."""
        if not v:
            raise ValueError('Terms of service must be accepted')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if len(v) > 128:
            raise ValueError('Password must not exceed 128 characters')
        
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
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate name field."""
        if not v.strip():
            raise ValueError('Name cannot be empty or contain only whitespace')
        
        # Check for invalid characters
        invalid_chars = ['<', '>', '&', '"', "'"]
        if any(char in v for char in invalid_chars):
            raise ValueError('Name contains invalid characters')
        
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "terms_accepted": True,
                "newsletter_enabled": True
            }
        }


class EmailVerificationRequest(BaseModel):
    """Request schema for email verification."""
    
    token: str = Field(
        ..., 
        description="Email verification token",
        min_length=1,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class ResendVerificationRequest(BaseModel):
    """Request schema for resending verification email."""
    
    email: EmailStr = Field(
        ..., 
        description="User email address",
        example="john.doe@example.com"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com"
            }
        }


class RegistrationResponse(BaseModel):
    """Response schema for successful registration."""
    
    message: str = Field(
        ..., 
        description="Success message",
        example="Registration successful. Please check your email for verification."
    )
    user: UserResponse = Field(..., description="Registered user information")
    verification_sent: bool = Field(
        ..., 
        description="Whether verification email was sent",
        example=True
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Registration successful. Please check your email for verification.",
                "verification_sent": True
            }
        }


class EmailVerificationResponse(BaseModel):
    """Response schema for successful email verification."""
    
    message: str = Field(
        ..., 
        description="Success message",
        example="Email verified successfully. Welcome to CraftyXhub!"
    )
    user: UserResponse = Field(..., description="Verified user information")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Email verified successfully. Welcome to CraftyXhub!"
            }
        }


class ResendVerificationResponse(BaseModel):
    """Response schema for resend verification."""
    
    message: str = Field(
        ..., 
        description="Response message",
        example="Verification email sent successfully"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Verification email sent successfully"
            }
        } 