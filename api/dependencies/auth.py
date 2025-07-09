"""
Authentication dependencies for CraftyXhub API

Following FastAPI OAuth2 with Password (and hashing), Bearer with JWT tokens tutorial exactly.
"""

from typing import Annotated, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
import jwt
from jwt.exceptions import InvalidTokenError

from core.config import settings
from core.security import SECRET_KEY, ALGORITHM, TokenData
from schemas.auth import User, UserInDB, UserRole
from models.user import User as UserModel
from dependencies.database import get_db

# OAuth2 scheme for token extraction - exactly as in FastAPI tutorial
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fake users database for tutorial - will be replaced with real database
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "testuser@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "disabled": False,
    }
}

def get_user(db: Session, username: str) -> Union[UserInDB, None]:
    """Get user from database - following FastAPI tutorial pattern."""
    # First check fake database for tutorial compatibility
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    
    # Then check real database (only if db is not None)
    if db is not None:
        try:
            statement = select(UserModel).where(UserModel.username == username)
            user = db.exec(statement).first()
            if user:
                return UserInDB(
                    username=user.username,
                    email=user.email,
                    full_name=user.name,
                    disabled=not user.is_active,
                    hashed_password=user.password_hash
                )
        except Exception:
            pass
    
    return None

def authenticate_user(db: Session, username: str, password: str) -> Union[UserInDB, bool]:
    """Authenticate user with username and password - exactly as in FastAPI tutorial."""
    from core.security import verify_password
    
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: Annotated[Session, Depends(get_db)]
) -> User:
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
    
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current active user - exactly as in FastAPI tutorial."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Legacy dependencies for backward compatibility
async def get_current_user_legacy(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> UserModel:
    """Legacy function - get current user as UserModel."""
    user = await get_current_user(token, db)
    
    # Convert to UserModel for legacy compatibility
    try:
        statement = select(UserModel).where(UserModel.username == user.username)
        db_user = db.exec(statement).first()
        if db_user:
            return db_user
    except Exception:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found in database"
    )

# Role-based access control - following FastAPI best practices
def require_role(required_role: UserRole):
    """Dependency factory for role-based access control."""
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
    """Dependency factory for multiple role access control."""
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

# Specific role dependencies - following FastAPI best practices
require_admin = require_role(UserRole.ADMIN)
require_editor = require_role(UserRole.EDITOR)
require_user = require_role(UserRole.USER)

# Combined role dependencies
require_admin_or_editor = require_roles(UserRole.ADMIN, UserRole.EDITOR)
require_any_role = require_roles(UserRole.USER, UserRole.EDITOR, UserRole.ADMIN)

def require_user_or_admin(user_id: int):
    """Dependency that requires the user to be the owner or an admin."""
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
    """Dependency that requires at least the specified role level."""
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