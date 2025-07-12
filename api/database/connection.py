from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
import logging
from core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
DATABASE_URL = settings.get_database_config()["url"]

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


async def get_db_session():
    """
    Provide an async database session for dependency injection.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """
    Initialize database by creating all tables defined in SQLModel models.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)  # Use SQLModel.metadata
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def db_health_check() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def drop_all_tables(self) -> None:
    if not self._initialized:
        raise RuntimeError("Database manager not initialized")

    async with self.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    logger.warning("All database tables dropped")


async def close_db() -> None:
    try:
        await engine.dispose()
        logger.info("Database engine closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


class DatabaseTransaction:

    def __init__(self):
        self.session = None

    async def __aenter__(self) -> AsyncSession:
        self.session = await get_db_session()
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