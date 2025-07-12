
from typing import Annotated, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt
from jwt.exceptions import InvalidTokenError

from core.config import get_settings
from core.security import SECRET_KEY, ALGORITHM, TokenData
from schemas.auth import User, UserInDB, UserRole
from models.user import User as UserModel
from dependencies.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_user(db: AsyncSession, username: str) -> Union[UserInDB, None]:
    try:
        statement = select(UserModel).where(UserModel.email == username)
        result = await db.execute(statement)
        user = result.scalar_one_or_none()
        if user:
            return UserInDB(
                username=user.email,
                email=user.email,
                full_name=user.name,
                disabled=False,  # No is_active column, so always enabled
                hashed_password=user.password_hash
            )
    except Exception:
        pass
    
    return None

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Union[UserInDB, bool]:
    from core.security import verify_password
    
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
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
    
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_user_legacy(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserModel:
    user = await get_current_user(token, db)
    
    try:
        statement = select(UserModel).where(UserModel.email == user.username)
        result = await db.execute(statement)
        db_user = result.scalar_one_or_none()
        if db_user:
            return db_user
    except Exception:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found in database"
    )

def require_role(required_role: UserRole):
    async def role_checker(
        current_user: Annotated[UserModel, Depends(get_current_user_legacy)]
    ) -> UserModel:
        if current_user.role != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role.value} role"
            )
        return current_user
    return role_checker

def require_roles(*allowed_roles: UserRole):
    async def roles_checker(
        current_user: Annotated[UserModel, Depends(get_current_user_legacy)]
    ) -> UserModel:
        allowed_role_values = [role.value for role in allowed_roles]
        if current_user.role not in allowed_role_values:
            roles_str = " or ".join(allowed_role_values)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {roles_str} role"
            )
        return current_user
    return roles_checker

require_admin = require_role(UserRole.ADMIN)
require_editor = require_role(UserRole.EDITOR)
require_user = require_role(UserRole.USER)

require_admin_or_editor = require_roles(UserRole.ADMIN, UserRole.EDITOR)
require_any_role = require_roles(UserRole.USER, UserRole.EDITOR, UserRole.ADMIN)

def require_user_or_admin(user_id: int):
    async def user_or_admin_checker(
        current_user: Annotated[UserModel, Depends(get_current_user_legacy)]
    ) -> UserModel:
        if current_user.id != user_id and current_user.role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient permissions"
            )
        return current_user
    return user_or_admin_checker

def require_minimum_role(minimum_role: UserRole):   
    role_hierarchy = {
        UserRole.USER: 1,
        UserRole.EDITOR: 2,
        UserRole.ADMIN: 3
    }
    
    async def minimum_role_checker(
        current_user: Annotated[UserModel, Depends(get_current_user_legacy)]
    ) -> UserModel:
        user_role_level = role_hierarchy.get(UserRole(current_user.role), 0)
        required_level = role_hierarchy.get(minimum_role, 999)
        
        if user_role_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires minimum {minimum_role.value} role"
            )
        return current_user
    return minimum_role_checker 