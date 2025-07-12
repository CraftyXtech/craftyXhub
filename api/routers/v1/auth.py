

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token, 
    create_refresh_token,
    verify_token,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse
)
from dependencies.auth import authenticate_user, get_current_active_user, oauth2_scheme
from dependencies.database import get_db
from schemas.auth import Token, User, LogoutRequest
from models.user import User as UserModel
from sqlalchemy import select

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Authentication"])
# Note: Exception handler is managed at the app level in main.py

@router.post("/token", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> LoginResponse:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get full user data for response
    statement = select(UserModel).where(UserModel.email == user.username)
    result = await db.execute(statement)
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in database",
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(user.username)
    
    # Prepare user data for response
    user_data = {
        "id": db_user.id,
        "username": db_user.email,  # Use email as username
        "email": db_user.email,
        "full_name": db_user.name,
        "disabled": False,  # No is_active column, so always enabled
        "is_verified": bool(db_user.email_verified_at),  # True if email_verified_at is not None
        "created_at": db_user.created_at.isoformat() if hasattr(db_user, 'created_at') else None,
        "updated_at": db_user.updated_at.isoformat() if hasattr(db_user, 'updated_at') else None
    }
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_data
    )

@router.post("/refresh", response_model=RefreshTokenResponse)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> RefreshTokenResponse:
    try:
        # Verify refresh token
        payload = verify_token(refresh_request.refresh_token, "refresh")
        username = payload.get("sub")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        # Verify user still exists in database
        statement = select(UserModel).where(UserModel.email == username)
        result = await db.execute(statement)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        
        # Create new refresh token (token rotation)
        new_refresh_token = create_refresh_token(username)
        
        return RefreshTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

@router.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    return current_user

@router.post("/logout")
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    logout_request: LogoutRequest,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    # For simplified approach, we'll just return success

    return {"message": "Successfully logged out"}

# Legacy endpoints for backward compatibility
@router.post("/login")
async def login_legacy(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    return await login_for_access_token(request, form_data, db)

@router.get("/me")
async def get_current_user_legacy(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return await read_users_me(current_user) 