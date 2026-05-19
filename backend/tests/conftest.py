import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from app.main import app
from app.database import get_db, Base
from app.config import settings
from app.models.user import User
from app.models.enums import UserRole
from app.utils.security import get_password_hash

# Use a test database URL or append _test to avoid wiping production data
# For local dev, we will safely drop and create tables per test session
TEST_DATABASE_URL = settings.DATABASE_URL + "_test"

engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session")
async def setup_test_db():
    """Create all tables for DB-backed tests, or skip them when Postgres is unavailable."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    except OSError as exc:
        pytest.skip(f"PostgreSQL test database is unavailable: {exc}", allow_module_level=True)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(setup_test_db) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session for each test."""
    async with TestingSessionLocal() as session:
        yield session
        # Clean up data after each test to ensure isolation
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client for API endpoints."""

    # Override the get_db dependency to use our test session
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_owner(db_session: AsyncSession) -> User:
    """Fixture to create a test owner user."""
    user = User(
        email="owner@tablewise.com",
        full_name="Test Owner",
        phone_number="0700000000",
        role=UserRole.OWNER,
        hashed_password=get_password_hash("testpassword123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user