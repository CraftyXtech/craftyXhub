

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from core.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from dependencies.auth import authenticate_user, get_current_active_user
from dependencies.database import get_db
from schemas.auth import Token, User

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
) -> Token:
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    
    return current_user

@router.get("/users/me/items")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    
    return [{"item_id": "Foo", "owner": current_user.username}]

# Legacy endpoints for backward compatibility
@router.post("/login")
async def login_legacy(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    
    return await login_for_access_token(form_data, db)

@router.get("/me")
async def get_current_user_legacy(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    
    return await read_users_me(current_user)

@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    
    return {"message": "Successfully logged out"} 