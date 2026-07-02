import pytest
from httpx import AsyncClient
from app.models.user import User
from app.config import settings
from app.utils.jwt import create_access_token


@pytest.mark.asyncio
async def test_inventory_lifecycle(async_client: AsyncClient, test_owner: User):
    """Integration test: Create outlet, add inventory, update stock."""
    token = create_access_token(subject=str(test_owner.id), role=test_owner.role)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create an Outlet (needed for inventory foreign key)
    branch_payload = {"name": "Westlands", "location": "Westlands", "contact_number": "0722000000"}
    branch_resp = await async_client.post(f"{settings.API_V1_STR}/branches/", json=branch_payload, headers=headers)
    assert branch_resp.status_code == 201
    outlet_id = branch_resp.json()["id"]

    # 2. Create Inventory Item (schema requires outlet_id, not branch_id)
    inv_payload = {
        "name": "Cooking Oil",
        "unit": "Liters",
        "quantity": 10.0,
        "outlet_id": outlet_id,
    }
    inv_resp = await async_client.post(f"{settings.API_V1_STR}/inventory/", json=inv_payload, headers=headers)
    assert inv_resp.status_code == 201
    item_id = inv_resp.json()["id"]
    assert inv_resp.json()["quantity"] == 10.0

    # 3. Adjust Stock
    adjust_payload = {"quantity_added": -2.5}  # e.g., used 2.5 Liters
    adj_resp = await async_client.patch(f"{settings.API_V1_STR}/inventory/{item_id}/stock", json=adjust_payload,
                                        headers=headers)
    assert adj_resp.status_code == 200
    assert adj_resp.json()["quantity"] == 7.5
