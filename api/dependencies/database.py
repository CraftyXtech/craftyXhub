"""
Database dependencies for FastAPI dependency injection.
Implements SubPRD-DependencyInjection.md specifications.
"""
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get database session.
    
    Usage:
        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    
    Yields:
        AsyncSession: Database session with automatic cleanup
    """
    async for session in get_db_session():
        yield session


# Alias for backward compatibility and cleaner imports
get_database = get_db 