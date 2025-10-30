import os
import sys
import pathlib
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Ensure API package is importable (add /api to sys.path)
API_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))

from main import create_application  # type: ignore
from database.connection import get_db_session  # type: ignore
from services.user.auth import get_current_active_user  # type: ignore
from models.base import Base as ModelsBase  # type: ignore
from models.user import User, UserRole  # type: ignore


TEST_DB_URL = "sqlite+aiosqlite:///./test_api.sqlite3"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(ModelsBase.metadata.create_all)
    yield engine
    try:
        async with engine.begin() as conn:
            await conn.run_sync(ModelsBase.metadata.drop_all)
    finally:
        await engine.dispose()
        # Cleanup sqlite file
        try:
            os.remove("test_api.sqlite3")
        except Exception:
            pass


@pytest_asyncio.fixture
async def test_session(test_engine):
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=True
    )
    async with async_session() as session:
        yield session
        # Reset DB between tests
        await session.rollback()
        async with test_engine.begin() as conn:
            await conn.run_sync(ModelsBase.metadata.drop_all)
            await conn.run_sync(ModelsBase.metadata.create_all)


@pytest_asyncio.fixture
async def author_user(test_session: AsyncSession) -> User:
    user = User(
        email="author@example.com",
        username="author",
        full_name="Author User",
        password="hashed",
        role=UserRole.USER,
        is_active=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(test_session: AsyncSession) -> User:
    user = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        password="hashed",
        role=UserRole.ADMIN,
        is_active=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


def make_db_override(session: AsyncSession):
    async def _override():
        try:
            yield session
        finally:
            pass
    return _override


def _make_auth_override(user: User):
    async def _override():
        return user
    return _override


@pytest_asyncio.fixture
async def client_author(test_session: AsyncSession, author_user: User):
    app = create_application()
    app.dependency_overrides[get_db_session] = make_db_override(test_session)
    app.dependency_overrides[get_current_active_user] = _make_auth_override(author_user)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def client_admin(test_session: AsyncSession, admin_user: User):
    app = create_application()
    app.dependency_overrides[get_db_session] = make_db_override(test_session)
    app.dependency_overrides[get_current_active_user] = _make_auth_override(admin_user)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
