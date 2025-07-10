"""
CraftyXhub API Schemas

This module contains all Pydantic schemas for request/response validation
and serialization in the CraftyXhub FastAPI application.
"""

# Authentication schemas - FastAPI tutorial
from .auth import (
    Token,
    TokenData,
    User,
    UserInDB,
    UserLogin,
    UserCreate,
    UserUpdate,
    UserResponse,
    # Legacy schemas for backward compatibility
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
    TokenValidationResponse,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    TwoFactorLoginRequest,
    PasswordStrengthResponse,
    OAuthLoginRequest,
    OAuthLinkRequest,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyList
)

# User registration schemas
from .registration import (
    UserRegistration,
    RegistrationResponse,
    EmailVerificationRequest as EmailVerificationRequestReg,
    EmailVerificationResponse
)

# Password management schemas
from .password import (
    PasswordResetRequest as PasswordResetRequestPwd,
    PasswordResetConfirm as PasswordResetConfirmPwd,
    PasswordChange,
    PasswordConfirm
)

__all__ = [
    # FastAPI Tutorial Authentication
    "Token",
    "TokenData", 
    "User",
    "UserInDB",
    "UserLogin",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    
    # Legacy Authentication
    "LoginRequest",
    "LoginResponse", 
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "LogoutRequest",
    "TokenValidationResponse",
    "PasswordChangeRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "EmailVerificationRequest",
    "TwoFactorSetupResponse",
    "TwoFactorVerifyRequest",
    "TwoFactorLoginRequest",
    "PasswordStrengthResponse",
    "OAuthLoginRequest",
    "OAuthLinkRequest",
    "APIKeyCreate",
    "APIKeyResponse",
    "APIKeyList",
    
    # Registration
    "UserRegistration",
    "RegistrationResponse",
    "EmailVerificationRequestReg", 
    "EmailVerificationResponse",
    
    # Password Management
    "PasswordResetRequestPwd",
    "PasswordResetConfirmPwd",
    "PasswordChange",
    "PasswordConfirm"
] 