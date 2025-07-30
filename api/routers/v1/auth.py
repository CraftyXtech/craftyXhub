import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta, timezone
from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse, Token, ResetPasswordRequest
from services.user.auth import AuthService, get_current_active_user
from database.connection import get_db_session


router = APIRouter(prefix="/auth", tags=["authentication"])
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30) 


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    existing_user = await AuthService.get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await AuthService.get_user_by_username(session, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    hashed_password = AuthService.get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password=hashed_password
    )
    
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    session: AsyncSession = Depends(get_db_session)
):
    user = await AuthService.authenticate_user(
        session, user_credentials.email, user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    user.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()
    
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(ACCESS_TOKEN_EXPIRE_MINUTES) * 60
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    
    user_data = {
        "uuid": current_user.uuid,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "role": current_user.role,
        "last_login": current_user.last_login,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }
    return user_data

@router.get("/user/{user_uuid}", response_model=UserResponse)
async def get_user_by_uuid(
    user_uuid: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    user = await AuthService.get_user_by_uuid(session, user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    return user

@router.put("/user/{user_uuid}", response_model=UserResponse)
async def update_user_profile(
    user_uuid: str,
    full_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    user = await AuthService.get_user_by_uuid(session, user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    if full_name:
        user.full_name = full_name
    
    user.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()
    await session.refresh(user)
    
    return user

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": "Successfully logged out"}

@router.put("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session)
):
    if request.new_password != request.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    if not AuthService.verify_password(request.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    current_user.password = AuthService.get_password_hash(request.new_password)
    current_user.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()
    
    return {"message": "Password updated successfully"}