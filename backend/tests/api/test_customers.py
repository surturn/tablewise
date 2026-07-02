import pytest
from httpx import AsyncClient
from app.config import settings
from app.models.user import User
from app.utils.jwt import create_access_token


@pytest.mark.asyncio
async def test_customer_registration_and_login(async_client: AsyncClient, test_owner: User):
    """Integration test: Ensure staff-facing guest 'get_or_create' logic works correctly.

    /customers/ is a staff-only endpoint (create_guest role-gated in app/routers/customers.py)
    that get-or-creates a Guest by phone number; it is not a public self-service registration
    endpoint (that flow lives at /auth/customer/register, see app/routers/customer_auth.py).
    """
    token = create_access_token(subject=str(test_owner.id), role=test_owner.role)
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "phone_number": "0711223344",
        "full_name": "Jane Doe",
        "email": "jane@example.com",
    }

    # 1. First request creates the guest
    response_1 = await async_client.post(f"{settings.API_V1_STR}/customers/", json=payload, headers=headers)
    assert response_1.status_code == 201
    data_1 = response_1.json()
    assert "id" in data_1
    assert data_1["loyalty_points"] == 0

    customer_id = data_1["id"]

    # 2. Second request with the same phone number returns the same guest (no duplicate)
    response_2 = await async_client.post(f"{settings.API_V1_STR}/customers/", json=payload, headers=headers)
    assert response_2.status_code == 201
    data_2 = response_2.json()
    assert data_2["id"] == customer_id
