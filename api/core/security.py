

from datetime import datetime, timedelta, timezone
from typing import Annotated, Union, Optional

import jwt
import secrets
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


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
   
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
   
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
   
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]):
   
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
    return token_data

async def get_current_active_user_from_token(
    current_user: Annotated[UserInToken, Depends(get_current_user_from_token)],
):
   
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def hash_password(password: str) -> str:
    return get_password_hash(password)

def verify_token(token: str, token_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )


blacklisted_tokens = set()

def blacklist_token(token: str) -> None:
       blacklisted_tokens.add(token)

def is_token_blacklisted(token: str) -> bool:
        return token in blacklisted_tokens


def generate_verification_token(token_type: str, length: int = 32) -> str:
    """
    Generate a secure random token for email verification, password reset, etc.
    
    Args:
        token_type: Type of token (e.g., 'email_verification', 'password_reset')
        length: Length of the token in bytes (default 32)
    
    Returns:
        Hex-encoded secure random token
    """
    return secrets.token_hex(length) 