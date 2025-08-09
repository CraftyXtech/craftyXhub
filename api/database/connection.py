from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
import logging
from core.config import settings
from typing import AsyncGenerator, Any, List
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()

# engine = create_async_engine(
#     settings.DATABASE_URL,
#     pool_size=5,
#     max_overflow=10,
#     pool_timeout=30,
#     pool_pre_ping=True,
# )
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def db_health_check() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def drop_all_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("All database tables dropped")


async def close_db() -> None:
    try:
        await engine.dispose()
        logger.info("Database engine closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


class DatabaseTransaction:
    def __init__(self):
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> AsyncSession:
        self.session = AsyncSessionLocal()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            try:
                if exc_type is None:
                    await self.session.commit()
                else:
                    await self.session.rollback()
            finally:
                await self.session.close()


async def execute_query(query: str, params: dict | None = None) -> Any:
    async with DatabaseTransaction() as session:
        result = await session.execute(text(query), params or {})
        return result


async def bulk_insert(objects: List[Any]) -> None:
    async with DatabaseTransaction() as session:
        session.add_all(objects)


async def bulk_update(model_class: Any, updates: List[dict]) -> None:
    async with DatabaseTransaction() as session:
        for update_data in updates:
            record_id = update_data.pop('id')
            stmt = (
                model_class.__table__.update()
                .where(model_class.__table__.c.id == record_id)
                .values(**update_data)
            )
            await session.execute(stmt)


async def get_session() -> AsyncSession:
    return AsyncSessionLocal()


async def execute_with_session(session: AsyncSession, query: str, params: dict | None = None) -> Any:
    return await session.execute(text(query), params or {})