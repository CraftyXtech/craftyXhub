from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
import logging

from core.config import get_settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.async_session_factory = None
        self._initialized = False
    
    def initialize(self) -> None:
        if self._initialized:
            logger.warning("Database manager already initialized")
            return
        
        settings = get_settings()
        
        db_config = settings.get_database_config()
        db_url = db_config["url"]
        
        engine_args = {
            "echo": db_config.get("echo", settings.debug),
        }
        
        if "connect_args" in db_config:
            engine_args["connect_args"] = db_config["connect_args"]
        
        engine_args.update({
            "pool_size": db_config.get("pool_size", 5),
            "max_overflow": db_config.get("max_overflow", 10),
            "pool_timeout": db_config.get("pool_timeout", 30),
            "pool_recycle": db_config.get("pool_recycle", 3600),  
            "pool_pre_ping": db_config.get("pool_pre_ping", True),  
        })
        
        # Create async engine
        self.engine = create_async_engine(db_url, **engine_args)
        
        self.async_session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False,
        )
        
        self._initialized = True
        logger.info("Database manager initialized successfully")
    
    async def create_all_tables(self) -> None:
        """
        Create all database tables based on SQLModel definitions.
        Should be called during application startup after models are imported.
        """
        if not self._initialized:
            raise RuntimeError("Database manager not initialized")
        
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        logger.info("Database tables created successfully")
    
    async def drop_all_tables(self) -> None:
        """
        Drop all database tables. Use with caution!
        Primarily for testing and development.
        """
        if not self._initialized:
            raise RuntimeError("Database manager not initialized")
        
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        
        logger.warning("All database tables dropped")
    
    async def get_session(self) -> AsyncSession:
        """
        Get a new database session.
        Returns an AsyncSession instance for database operations.
        """
        if not self._initialized:
            raise RuntimeError("Database manager not initialized")
        
        return self.async_session_factory()
    
    async def close(self) -> None:
        """
        Close database engine and cleanup connections.
        Should be called during application shutdown.
        """
        if self.engine:
            await self.engine.dispose()
            logger.info("Database engine closed")
        
        self._initialized = False
    
    async def health_check(self) -> bool:
        """
        Perform a database health check.
        Returns True if database is accessible, False otherwise.
        """
        try:
            async with self.get_session() as session:
                # Simple query to test connection
                from sqlalchemy import text
                result = await session.exec(text("SELECT 1"))
                return result is not None
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.get_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database() -> None:
    
    try:
        db_manager.initialize()
        from models import user, post, category, tag, comment, interactions
        
        await db_manager.create_all_tables()
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_database() -> None:
    try:
        await db_manager.close()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


async def check_database_health() -> bool:
    
    return await db_manager.health_check()


class DatabaseTransaction:
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self) -> AsyncSession:
        """Enter transaction context."""
        self.session = await db_manager.get_session()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context with proper cleanup."""
        if self.session:
            try:
                if exc_type is None:
                    await self.session.commit()
                else:
                    await self.session.rollback()
            finally:
                await self.session.close()


# Utility functions for common database operations

async def execute_query(query: str, **params) -> any:
    async with DatabaseTransaction() as session:
        result = await session.exec(query, params)
        return result


async def bulk_insert(objects: list) -> None:
    async with DatabaseTransaction() as session:
        session.add_all(objects)


async def bulk_update(model_class, updates: list) -> None:
    async with DatabaseTransaction() as session:
        for update_data in updates:
            await session.exec(
                model_class.__table__.update().values(**update_data)
            ) 