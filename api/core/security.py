"""
Security utilities for CraftyXhub API

JWT token management, password hashing, and authentication utilities
following FastAPI OAuth2 with Password (and hashing), Bearer with JWT tokens tutorial exactly.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated, Union, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from core.config import settings

# to get a string like this run: openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction - exactly as in FastAPI tutorial
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class UserInToken(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash - exactly as in FastAPI tutorial."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt - exactly as in FastAPI tutorial."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """Create JWT access token - exactly as in FastAPI tutorial."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]):
    """Get current user from JWT token - exactly as in FastAPI tutorial."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    
    # This will be replaced by database lookup in dependencies/auth.py
    return token_data

async def get_current_active_user_from_token(
    current_user: Annotated[UserInToken, Depends(get_current_user_from_token)],
):
    """Get current active user - exactly as in FastAPI tutorial."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Legacy functions for backward compatibility (will be removed later)
def hash_password(password: str) -> str:
    """Legacy function - use get_password_hash instead."""
    return get_password_hash(password)

def verify_token(token: str, token_type: str = "access") -> dict:
    """Legacy function - simplified for compatibility."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

# Simplified blacklisting for now (can be enhanced later)
blacklisted_tokens = set()

def blacklist_token(token: str) -> None:
    """Simple token blacklisting - can be enhanced with Redis later."""
    blacklisted_tokens.add(token)

def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted."""
    return token in blacklisted_tokens 