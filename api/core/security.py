"""
Security utilities for CraftyXhub API

JWT token management, password hashing, and authentication utilities
following SubPRD-JWTAuthentication.md and SubPRD-PasswordManagement.md specifications.
"""

import secrets
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import redis
from core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Redis client for token blacklisting (lazy initialization)
redis_client = None

def get_redis_client():
    """Get Redis client with lazy initialization."""
    global redis_client
    if redis_client is None:
        # For now, use default Redis settings
        # TODO: Get Redis config from settings.config.get_cache_config()
        redis_client = redis.Redis(
            host="localhost",
            port=6379,
            password=None,
            db=0,
            decode_responses=True
        )
    return redis_client


class SecurityManager:
    """Central security manager for authentication and authorization."""
    
    # JWT Configuration as per PRD specifications
    ALGORITHM = "RS256"  # RSA with SHA-256
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    TOKEN_ISSUER = "craftyhub"
    
    def __init__(self):
        """Initialize security manager with RSA keys."""
        self.private_key = self._get_private_key()
        self.public_key = self._get_public_key()
    
    def _get_private_key(self) -> str:
        """Get RSA private key for token signing."""
        if hasattr(settings, 'JWT_PRIVATE_KEY'):
            return settings.JWT_PRIVATE_KEY
        
        # For development, generate a simple key
        # In production, this should come from environment/vault
        return """-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----"""
    
    def _get_public_key(self) -> str:
        """Get RSA public key for token verification."""
        if hasattr(settings, 'JWT_PUBLIC_KEY'):
            return settings.JWT_PUBLIC_KEY
        
        # For development, generate a simple key
        # In production, this should come from environment/vault
        return """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2K5PQmUrB5QHdQ3oJd5q
Ov6mGZHjl/HNYcMnF7VlImOtMLdV7x8XpU9R0qPUeZCdN8/PQgD2L4wFjWqZzXHm
3JcL8FdRx2RlNk4aF5qE9C3sKfBwQdWqXhFvH8LdGjGxZ7VlLzRv0jD3PmNqOhCw
1vXqPzFf2QkLqE4Z0cMcGlHsVx4k5j8XpRqN3Q8nWdL7YjHfGZPWvZqRcAo1R6Vl
KcQ8DxLqPmGsZ0qOeH1Fv7QdLUkN9RjKdZKdRcXlVz4ePmQvJsKvC9fAqHjKqRcF
dUoXcSQhNwFpQzL6R4YjHbGVcFdKjEfO4pRqVlQjKdGhLsRcNjQvKmGzMqFpQzEw
IDAQAB
-----END PUBLIC KEY-----"""
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def generate_tokens(self, user_id: str, email: str, role: str, remember_me: bool = False) -> Dict[str, Any]:
        """Generate access and refresh tokens for user."""
        now = datetime.now(timezone.utc)
        
        # Access token (15 minutes)
        access_exp = now + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "exp": access_exp,
            "iat": now,
            "iss": self.TOKEN_ISSUER,
            "type": "access"
        }
        
        # Refresh token (7 days, or longer if remember_me)
        refresh_days = self.REFRESH_TOKEN_EXPIRE_DAYS
        if remember_me:
            refresh_days = 30  # 30 days for "remember me"
        
        refresh_exp = now + timedelta(days=refresh_days)
        refresh_payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "exp": refresh_exp,
            "iat": now,
            "iss": self.TOKEN_ISSUER,
            "type": "refresh"
        }
        
        access_token = jwt.encode(access_payload, self.private_key, algorithm=self.ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, self.private_key, algorithm=self.ALGORITHM)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            # Check if token is blacklisted
            if self.is_token_blacklisted(token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.ALGORITHM],
                options={"verify_exp": True, "verify_iss": True}
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Verify issuer
            if payload.get("iss") != self.TOKEN_ISSUER:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token issuer",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def blacklist_token(self, token: str) -> None:
        """Add token to blacklist for secure logout."""
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.ALGORITHM],
                options={"verify_exp": False}  # Don't verify expiration for blacklisting
            )
            
            # Calculate TTL based on token expiration
            exp = payload.get("exp")
            if exp:
                exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
                ttl = int((exp_datetime - datetime.now(timezone.utc)).total_seconds())
                if ttl > 0:
                    # Store token in Redis with TTL
                    client = get_redis_client()
                    client.setex(f"blacklist:{token}", ttl, "1")
        except Exception:
            # If we can't decode the token, blacklist it indefinitely
            client = get_redis_client()
            client.set(f"blacklist:{token}", "1")
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        try:
            client = get_redis_client()
            return client.exists(f"blacklist:{token}") > 0
        except redis.RedisError:
            # If Redis is unavailable, assume token is not blacklisted
            # In production, you might want to fail secure and deny access
            return False
    
    def blacklist_all_user_tokens(self, user_id: str) -> None:
        """Blacklist all tokens for a specific user."""
        # This would require storing user tokens in Redis
        # For now, we'll implement a simple pattern-based approach
        pattern = f"user_tokens:{user_id}:*"
        try:
            client = get_redis_client()
            keys = client.keys(pattern)
            if keys:
                for key in keys:
                    token = client.get(key)
                    if token:
                        self.blacklist_token(token)
                # Clean up user token tracking
                client.delete(*keys)
        except redis.RedisError:
            pass
    
    def generate_verification_token(self, purpose: str = "email_verification", length: int = 64) -> str:
        """Generate secure random token for email verification or password reset."""
        return secrets.token_urlsafe(length)
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength according to PRD requirements."""
        feedback = []
        requirements_met = {
            "min_length": len(password) >= 8,
            "has_uppercase": any(c.isupper() for c in password),
            "has_lowercase": any(c.islower() for c in password),
            "has_number": any(c.isdigit() for c in password),
            "has_special_char": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        }
        
        score = 0
        
        # Length scoring
        if len(password) >= 8:
            score += 20
        elif len(password) >= 6:
            score += 10
            feedback.append("Password should be at least 8 characters long")
        else:
            feedback.append("Password is too short (minimum 8 characters)")
        
        # Character type scoring
        if requirements_met["has_uppercase"]:
            score += 20
        else:
            feedback.append("Add at least one uppercase letter")
        
        if requirements_met["has_lowercase"]:
            score += 20
        else:
            feedback.append("Add at least one lowercase letter")
        
        if requirements_met["has_number"]:
            score += 20
        else:
            feedback.append("Add at least one number")
        
        if requirements_met["has_special_char"]:
            score += 20
        else:
            feedback.append("Add at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
        
        # Length bonus
        if len(password) >= 12:
            score += 10
        elif len(password) >= 10:
            score += 5
        
        # Complexity bonus (entropy)
        unique_chars = len(set(password))
        if unique_chars >= len(password) * 0.8:
            score += 10
        elif unique_chars >= len(password) * 0.6:
            score += 5
        
        if len(password) >= 16:
            feedback.append("Excellent password length!")
        elif len(password) >= 12:
            feedback.append("Good password length")
        
        is_strong = all(requirements_met.values())
        
        return {
            "is_strong": is_strong,
            "score": min(score, 100),
            "feedback": feedback,
            "requirements_met": requirements_met
        }


# Global security manager instance
security = SecurityManager()


# Convenience functions for backward compatibility
def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return security.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return security.verify_password(plain_password, hashed_password)


def generate_tokens(user_id: str, email: str, role: str, remember_me: bool = False) -> Dict[str, Any]:
    """Generate access and refresh tokens for user."""
    return security.generate_tokens(user_id, email, role, remember_me)


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Verify and decode JWT token."""
    return security.verify_token(token, token_type)


def blacklist_token(token: str) -> None:
    """Add token to blacklist for secure logout."""
    return security.blacklist_token(token)


def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted."""
    return security.is_token_blacklisted(token)


def generate_verification_token(purpose: str = "email_verification", length: int = 64) -> str:
    """Generate secure random token for email verification or password reset."""
    return security.generate_verification_token(purpose, length) 