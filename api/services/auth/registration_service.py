import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from models.user import User, UserPreference
from schemas.registration import UserRegistration
from schemas.user import UserResponse
from core.exceptions import UserAlreadyExistsError, UserNotFoundError

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegistrationService:
    """Registration service for handling user registration flow."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    async def check_user_exists(db: AsyncSession, email: str) -> None:
        """Check if user already exists by email."""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise UserAlreadyExistsError("Email already registered")
    
    @staticmethod
    async def create_user_record(db: AsyncSession, user_data: UserRegistration) -> User:
        """Create new user record in database."""
        await RegistrationService.check_user_exists(db, user_data.email)
        
        # Hash password
        hashed_password = RegistrationService.hash_password(user_data.password)
        
        # Create user
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            role="user",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(new_user)
        await db.flush()  # Get the ID without committing
        await db.refresh(new_user)
        
        # Create user preferences if newsletter setting provided
        if hasattr(user_data, 'newsletter_enabled'):
            user_preference = UserPreference(
                user_id=new_user.id,
                newsletter_enabled=user_data.newsletter_enabled,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(user_preference)
        
        return new_user
    
    @staticmethod
    async def register_user(
        db: AsyncSession, 
        user_data: UserRegistration,
        email_service,
        token_service
    ) -> UserResponse:
        """Complete user registration flow."""
        try:
            # Create user
            user = await RegistrationService.create_user_record(db, user_data)
            
            # Generate verification token
            verification_token = await token_service.create_verification_token(
                user.id, expiry_hours=24
            )
            
            # Send verification email
            await email_service.send_verification_email(
                email=user.email,
                token=verification_token,
                user_name=user.name
            )
            
            # Commit transaction
            await db.commit()
            
            logger.info(f"User registered successfully: {user.email}")
            
            return UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                avatar=user.avatar,
                bio=user.bio,
                is_active=True,
                is_verified=bool(user.email_verified_at),
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Registration failed for {user_data.email}: {str(e)}")
            raise
    
    @staticmethod
    async def verify_email(db: AsyncSession, token: str, token_service, email_service) -> UserResponse:
        """Verify user email with token."""
        # Validate and consume token
        token_data = await token_service.consume_token(token, "email_verification")
        
        # Get user from database
        stmt = select(User).where(User.id == token_data.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise UserNotFoundError("User not found")
        
        if user.email_verified_at:
            return UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                avatar=user.avatar,
                bio=user.bio,
                is_active=True,
                is_verified=True,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        
        # Update user verification status
        user.email_verified_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        # Send welcome email
        await email_service.send_welcome_email(
            email=user.email,
            user_name=user.name
        )
        
        logger.info(f"Email verified successfully for user: {user.email}")
        
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            avatar=user.avatar,
            bio=user.bio,
            is_active=True,
            is_verified=True,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    @staticmethod
    async def resend_verification(
        db: AsyncSession, 
        email: str, 
        token_service,
        email_service
    ) -> bool:
        """Resend verification email."""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise UserNotFoundError("User not found")
        
        if user.email_verified_at:
            return False  # Already verified
        
        # Revoke existing tokens
        await token_service.revoke_user_tokens(user.id, "email_verification")
        
        # Generate new verification token
        verification_token = await token_service.create_verification_token(
            user.id, expiry_hours=24
        )
        
        # Send verification email
        await email_service.send_verification_email(
            email=user.email,
            token=verification_token,
            user_name=user.name
        )
        
        logger.info(f"Verification email resent to: {user.email}")
        return True
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() 