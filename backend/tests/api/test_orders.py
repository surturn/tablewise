import pytest
from httpx import AsyncClient
from app.config import settings
from app.models.user import User
from app.models.enums import OrderStatus
from app.utils.jwt import create_access_token


@pytest.mark.asyncio
async def test_order_creation_and_state_machine(async_client: AsyncClient, test_owner: User):
    """Integration test: Verify order totals are calculated securely and strict state transitions."""
    token = create_access_token(subject=str(test_owner.id), role=test_owner.role)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Setup Prerequisites (Branch, Customer, Menu)
    branch_resp = await async_client.post(f"{settings.API_V1_STR}/branches/",
                                          json={"name": "Test", "location": "Test", "contact_number": "000"},
                                          headers=headers)
    branch_id = branch_resp.json()["id"]

    cust_resp = await async_client.post(f"{settings.API_V1_STR}/customers/",
                                        json={"phone_number": "0700111222", "full_name": "Test"})
    customer_id = cust_resp.json()["id"]

    cat_resp = await async_client.post(f"{settings.API_V1_STR}/menu/categories", json={"name": "Test Cat"},
                                       headers=headers)
    cat_id = cat_resp.json()["id"]

    item_resp = await async_client.post(f"{settings.API_V1_STR}/menu/items",
                                        json={"name": "Burger", "price": 500.0, "category_id": cat_id}, headers=headers)
    item_id = item_resp.json()["id"]

    # 2. Create Order
    order_payload = {
        "branch_id": branch_id,
        "customer_id": customer_id,
        "items": [
            {"menu_item_id": item_id, "quantity": 2}  # 2 * 500 = 1000
        ]
    }
    order_resp = await async_client.post(f"{settings.API_V1_STR}/orders/", json=order_payload, headers=headers)
    assert order_resp.status_code == 201
    order_data = order_resp.json()

    order_id = order_data["id"]
    assert order_data["status"] == OrderStatus.CREATED.value
    assert order_data["total_amount"] == 1000.0  # Backend calculated it correctly

    # 3. Test Invalid State Transition (CREATED -> DELIVERED should fail)
    invalid_patch = await async_client.patch(
        f"{settings.API_V1_STR}/orders/{order_id}/status",
        json={"status": OrderStatus.DELIVERED.value},
        headers=headers
    )
    assert invalid_patch.status_code == 400
    assert "Invalid state transition" in invalid_patch.json()["detail"]

    # 4. Test Valid State Transition (CREATED -> PENDING_PAYMENT should succeed)
    valid_patch = await async_client.patch(
        f"{settings.API_V1_STR}/orders/{order_id}/status",
        json={"status": OrderStatus.PENDING_PAYMENT.value},
        headers=headers
    )
    assert valid_patch.status_code == 200
    assert valid_patch.json()["status"] == OrderStatus.PENDING_PAYMENT.value