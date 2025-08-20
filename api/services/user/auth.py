import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models import User
from schemas.user import TokenData
from database.connection import get_db_session
from core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_uuid(session: AsyncSession, uuid: str) -> Optional[User]:
        statement = select(User).where(User.uuid == uuid)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def authenticate_user(session: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await AuthService.get_user_by_email(session, email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.password):
            return None
        return user

    @staticmethod
    async def login_with_social_profile(session: AsyncSession, email: str, name: Optional[str], picture: Optional[str], provider: str = "google") -> str:
        user = await AuthService.get_user_by_email(session, email)
        if not user:
            base_username = name or email.split('@')[0]
            full_name = name or email.split('@')[0]
            username = base_username
            counter = 1

            while True:
                existing_user = await session.execute(
                    select(User).where(User.username == username)
                )
                if not existing_user.scalar_one_or_none():
                    break
                username = f"{base_username}{counter}"
                counter += 1

            user = User(
                email=email,
                username=username,
                full_name=full_name,
                password=settings.GOOGLE_CLIENT_ID,  
                provider=provider,
                is_verified=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            if name:
                user.full_name = name
            user.last_login = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(user)

        token = AuthService._issue_jwt(user)
        return token



    @staticmethod
    def _issue_jwt(user: User) -> str:
        now = datetime.now(timezone.utc)
        exp_time = now + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))

        payload = {
            "sub": str(user.uuid),
            "email": user.email,
            "provider": user.provider,
            "iat": int(now.timestamp()),
            "exp": int(exp_time.timestamp())
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = await AuthService.get_user_by_email(session, email=token_data.email)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
