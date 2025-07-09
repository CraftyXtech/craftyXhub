"""
Authentication API Router for CraftyXhub

Authentication endpoints for login, token refresh, logout, and user information
following SubPRD-JWTAuthentication.md specifications.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from dependencies.database import get_db
from dependencies.auth import get_current_user, oauth2_scheme
from models.user import User
from schemas.auth import (
    LoginRequest, 
    LoginResponse, 
    TokenResponse, 
    RefreshTokenRequest,
    UserResponse,
    LogoutRequest,
    AuthError
)
from core.security import verify_token, blacklist_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user with email and password, return JWT tokens"
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    request: Request = None
) -> LoginResponse:
    """
    Authenticate user and return JWT tokens.
    
    - **email**: User email address
    - **password**: User password
    - **remember_me**: Extended session duration flag
    
    Returns user information and JWT tokens for API access.
    """
    # TODO: Implement rate limiting (5 attempts per IP per 15 minutes)
    
    # Get user by email
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not user.verify_password(login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate tokens (this will need to be implemented)
    # TODO: Implement token generation
    tokens = {
        "access_token": "placeholder_access_token",
        "refresh_token": "placeholder_refresh_token", 
        "token_type": "bearer",
        "expires_in": 900
    }
    
    # Update last login (if we add this field to User model)
    # user.last_login_at = datetime.now(timezone.utc)
    # await db.commit()
    
    return LoginResponse(
        user=UserResponse.model_validate(user),
        tokens=TokenResponse(**tokens)
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Token",
    description="Refresh access token using valid refresh token"
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Refresh access token using a valid refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access and refresh tokens.
    """
    try:
        # Verify refresh token
        payload = verify_token(refresh_data.refresh_token, "refresh")
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        
        if not all([user_id, email, role]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )
        
        # Verify user still exists and is active
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Generate new tokens (this will need to be implemented)
        # TODO: Implement token generation
        tokens = {
            "access_token": "placeholder_access_token",
            "refresh_token": "placeholder_refresh_token", 
            "token_type": "bearer",
            "expires_in": 900
        }
        
        # Blacklist the old refresh token
        blacklist_token(refresh_data.refresh_token)
        
        return TokenResponse(**tokens)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Logout user and blacklist tokens"
)
async def logout(
    logout_data: LogoutRequest = LogoutRequest(),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Logout user and blacklist current token.
    
    - **revoke_all_tokens**: Optional flag to revoke all user tokens
    
    Blacklists the current access token for secure logout.
    """
    try:
        # Blacklist current access token
        blacklist_token(credentials.credentials)
        
        # If requested, blacklist all user tokens (this will need to be implemented)
        if logout_data.revoke_all_tokens:
            # TODO: Implement blacklist_all_user_tokens function
            pass
        
        return {
            "message": "Successfully logged out",
            "tokens_revoked": "all" if logout_data.revoke_all_tokens else "current"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Current User Info",
    description="Get current authenticated user information"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get information about the currently authenticated user.
    
    Returns complete user profile information.
    """
    return UserResponse.model_validate(current_user)


@router.post(
    "/verify-token",
    status_code=status.HTTP_200_OK,
    summary="Verify Token",
    description="Verify if a token is valid and not blacklisted"
)
async def verify_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> dict:
    """
    Verify if an access token is valid.
    
    Returns token validity information and user claims.
    """
    try:
        payload = verify_token(credentials.credentials, "access")
        
        return {
            "valid": True,
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "expires_at": payload.get("exp"),
            "issued_at": payload.get("iat")
        }
        
    except HTTPException as e:
        return {
            "valid": False,
            "error": e.detail
        }


# Note: Exception handlers should be added to the main FastAPI app, not the router
# The core.exceptions module handles global exception handling 