import secrets
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any, Union
from uuid import UUID
import redis.asyncio as aioredis
from pydantic import BaseModel, Field
import logging

from core.config import get_settings
from core.exceptions import TokenValidationError, TokenExpiredError, TokenNotFoundError

logger = logging.getLogger(__name__)


class TokenData(BaseModel):
    user_id: UUID
    token_type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    expires_at: datetime


class TokenService:
    def __init__(self):
        self.settings = get_settings()
        self.redis_client: Optional[aioredis.Redis] = None
    
    async def get_redis_client(self) -> aioredis.Redis:
        """Get Redis client connection."""
        if not self.redis_client:
            self.redis_client = aioredis.from_url(
                self.settings.REDIS_URL,
                decode_responses=True
            )
        return self.redis_client
    
    def generate_token(self, length: int = 32) -> str:
        """Generate secure random token."""
        return secrets.token_urlsafe(length)
    
    def hash_token(self, token: str) -> str:
        """Hash token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def create_verification_token(
        self, 
        user_id: UUID, 
        expiry_hours: int = 24
    ) -> str:
        """Create email verification token."""
        token = self.generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
        
        token_data = TokenData(
            user_id=user_id,
            token_type="email_verification",
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at
        )
        
        await self._store_token(token, token_data)
        return token
    
    async def create_password_reset_token(
        self, 
        user_id: UUID, 
        expiry_hours: int = 1
    ) -> str:
        """Create password reset token."""
        token = self.generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
        
        token_data = TokenData(
            user_id=user_id,
            token_type="password_reset",
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at
        )
        
        await self._store_token(token, token_data)
        return token
    
    async def validate_token(self, token: str, expected_type: str) -> TokenData:
        """Validate token and return data."""
        token_data = await self._get_token(token)
        
        if not token_data:
            raise TokenNotFoundError("Token not found")
        
        if token_data.expires_at < datetime.now(timezone.utc):
            await self._delete_token(token)
            raise TokenExpiredError("Token has expired")
        
        if token_data.token_type != expected_type:
            raise TokenValidationError("Invalid token type")
        
        return token_data
    
    async def consume_token(self, token: str, expected_type: str) -> TokenData:
        """Validate and consume (delete) token."""
        token_data = await self.validate_token(token, expected_type)
        await self._delete_token(token)
        return token_data
    
    async def revoke_user_tokens(self, user_id: UUID, token_type: str) -> int:
        """Revoke all tokens of specific type for user."""
        redis = await self.get_redis_client()
        pattern = f"token:*"
        revoked_count = 0
        
        async for key in redis.scan_iter(match=pattern):
            token_json = await redis.get(key)
            if token_json:
                try:
                    data = json.loads(token_json)
                    if (data.get("user_id") == str(user_id) and 
                        data.get("token_type") == token_type):
                        await redis.delete(key)
                        revoked_count += 1
                except json.JSONDecodeError:
                    continue
        
        return revoked_count
    
    async def _store_token(self, token: str, token_data: TokenData) -> None:
        """Store token in Redis with expiration."""
        redis = await self.get_redis_client()
        key = f"token:{self.hash_token(token)}"
        
        # Serialize token data
        data = {
            "user_id": str(token_data.user_id),
            "token_type": token_data.token_type,
            "data": token_data.data,
            "created_at": token_data.created_at.isoformat(),
            "expires_at": token_data.expires_at.isoformat()
        }
        
        # Calculate TTL in seconds
        ttl = int((token_data.expires_at - datetime.now(timezone.utc)).total_seconds())
        
        await redis.setex(key, ttl, json.dumps(data))
        logger.debug(f"Token stored with key: {key}")
    
    async def _get_token(self, token: str) -> Optional[TokenData]:
        """Retrieve token data from Redis."""
        redis = await self.get_redis_client()
        key = f"token:{self.hash_token(token)}"
        
        token_json = await redis.get(key)
        if not token_json:
            return None
        
        try:
            data = json.loads(token_json)
            return TokenData(
                user_id=UUID(data["user_id"]),
                token_type=data["token_type"],
                data=data["data"],
                created_at=datetime.fromisoformat(data["created_at"]),
                expires_at=datetime.fromisoformat(data["expires_at"])
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error deserializing token data: {e}")
            await redis.delete(key)
            return None
    
    async def _delete_token(self, token: str) -> None:
        """Delete token from Redis."""
        redis = await self.get_redis_client()
        key = f"token:{self.hash_token(token)}"
        await redis.delete(key)
    
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens (Redis should handle this automatically)."""
        redis = await self.get_redis_client()
        pattern = f"token:*"
        cleaned_count = 0
        
        async for key in redis.scan_iter(match=pattern):
            if not await redis.exists(key):
                cleaned_count += 1
        
        return cleaned_count
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()


# Dependency injection
async def get_token_service() -> TokenService:
    return TokenService() 