import pytest
from httpx import AsyncClient
from app.config import settings


@pytest.mark.asyncio
async def test_customer_registration_and_login(async_client: AsyncClient):
    """Integration test: Ensure customer 'get_or_create' logic works correctly."""

    payload = {
        "phone_number": "0711223344",
        "full_name": "Jane Doe",
        "email": "jane@example.com"
    }

    # 1. First request creates the customer
    response_1 = await async_client.post(f"{settings.API_V1_STR}/customers/", json=payload)
    assert response_1.status_code == 200
    data_1 = response_1.json()
    assert "id" in data_1
    assert data_1["loyalty_points"] == 0

    customer_id = data_1["id"]

    # 2. Second request with the same phone number logs them in (returns same ID)
    response_2 = await async_client.post(f"{settings.API_V1_STR}/customers/", json=payload)
    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert data_2["id"] == customer_id  # Ensures no duplicate was created