import pytest
from httpx import AsyncClient
from app.models.user import User
from app.config import settings


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, test_owner: User):
    """Integration test: Verify valid credentials return a JWT."""
    login_data = {
        "username": "owner@tablewise.com",  # OAuth2 expects 'username' field
        "password": "testpassword123"
    }

    response = await async_client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_failure(async_client: AsyncClient, test_owner: User):
    """Integration test: Verify invalid credentials get rejected."""
    login_data = {
        "username": "owner@tablewise.com",
        "password": "wrongpassword"
    }

    response = await async_client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_get_me(async_client: AsyncClient, test_owner: User):
    """Integration test: Verify /me returns the current logged-in user details."""
    # 1. Login to get token
    login_data = {"username": test_owner.email, "password": "testpassword123"}
    login_response = await async_client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    # 2. Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)

    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == test_owner.email
    assert user_data["role"] == test_owner.role.value
    assert "password" not in user_data  # Ensure password is not leaked!