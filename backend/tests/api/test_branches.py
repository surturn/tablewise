import pytest
from httpx import AsyncClient
from app.models.user import User
from app.config import settings
from app.utils.jwt import create_access_token


@pytest.mark.asyncio
async def test_create_branch(async_client: AsyncClient, test_owner: User):
    """Integration test: Verify Owner can create a new branch."""
    token = create_access_token(subject=str(test_owner.id), role=test_owner.role)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": "Nairobi CBD",
        "location": "Kimathi Street",
        "contact_number": "0700111222",
        "opening_time": "07:00",
        "closing_time": "23:00"
    }

    response = await async_client.post(f"{settings.API_V1_STR}/branches/", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Nairobi CBD"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_list_branches_public(async_client: AsyncClient):
    """Integration test: Verify anyone can list branches (Public route)."""
    response = await async_client.get(f"{settings.API_V1_STR}/branches/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)