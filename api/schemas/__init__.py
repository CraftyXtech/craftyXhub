"""
CraftyXhub API Schemas

This module contains all Pydantic schemas for request/response validation
and serialization in the CraftyXhub FastAPI application.
"""

# Authentication schemas
from .auth import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    AuthError
)

# User registration schemas
from .registration import (
    UserRegistration,
    RegistrationResponse,
    EmailVerificationRequest,
    EmailVerificationResponse
)

# Password management schemas
from .password import (
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChange,
    PasswordConfirm
)

__all__ = [
    # Authentication
    "LoginRequest",
    "LoginResponse", 
    "TokenResponse",
    "RefreshTokenRequest",
    "UserResponse",
    "AuthError",
    
    # Registration
    "UserRegistration",
    "RegistrationResponse",
    "EmailVerificationRequest", 
    "EmailVerificationResponse",
    
    # Password Management
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordChange",
    "PasswordConfirm"
] 