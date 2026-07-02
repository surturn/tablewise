import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.customer import Guest
from app.rate_limit import limiter
from app.utils.security import get_password_hash


async def _setup_guest(db_session: AsyncSession) -> Guest:
    guest = Guest(
        phone_number="0700333444",
        full_name="Rate Limit Guest",
        email="ratelimit-guest@example.com",
        hashed_password=get_password_hash("correct-password"),
    )
    db_session.add(guest)
    await db_session.commit()
    return guest


@pytest.mark.asyncio
async def test_customer_login_rate_limited_after_repeated_attempts(async_client: AsyncClient, db_session: AsyncSession):
    """Integration test: brute-forcing /auth/customer/login gets blocked with 429 after the threshold."""
    limiter.reset()
    await _setup_guest(db_session)

    login_data = {"email": "ratelimit-guest@example.com", "password": "wrong-password"}

    for _ in range(5):
        response = await async_client.post(f"{settings.API_V1_STR}/auth/customer/login", json=login_data)
        assert response.status_code == 401

    blocked_response = await async_client.post(f"{settings.API_V1_STR}/auth/customer/login", json=login_data)
    assert blocked_response.status_code == 429

    limiter.reset()
