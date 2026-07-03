import pytest
from httpx import AsyncClient
from app.config import settings
from app.models.user import User
from app.models.enums import OrderStatus
from app.utils.jwt import create_access_token


@pytest.mark.asyncio
async def test_order_creation_and_state_machine(async_client: AsyncClient, test_owner: User):
    """Integration test: Verify order totals are calculated securely and strict state transitions.

    Orders are created guest-self-service (POST /orders/ requires a Guest JWT, see
    app/routers/orders.py::create_order) — guest_id is bound from the token, not the payload.
    """
    staff_token = create_access_token(subject=str(test_owner.id), role=test_owner.role)
    staff_headers = {"Authorization": f"Bearer {staff_token}"}

    # 1. Setup Prerequisites (Outlet, Menu) as staff
    branch_resp = await async_client.post(f"{settings.API_V1_STR}/branches/",
                                          json={"name": "Test", "location": "Test", "contact_number": "000"},
                                          headers=staff_headers)
    assert branch_resp.status_code == 201
    outlet_id = branch_resp.json()["id"]

    cat_resp = await async_client.post(f"{settings.API_V1_STR}/menu/categories", json={"name": "Test Cat"},
                                       headers=staff_headers)
    cat_id = cat_resp.json()["id"]

    item_resp = await async_client.post(
        f"{settings.API_V1_STR}/menu/items",
        json={"name": "Burger", "price_usd_cents": 50000, "category_id": cat_id, "outlet_id": outlet_id},
        headers=staff_headers,
    )
    assert item_resp.status_code == 201
    item_id = item_resp.json()["id"]

    # 2. Register a guest and authenticate as them
    guest_resp = await async_client.post(
        f"{settings.API_V1_STR}/auth/customer/register",
        json={"phone_number": "0700111222", "full_name": "Test Guest", "email": "guest@example.com", "password": "guestpass123"},
    )
    assert guest_resp.status_code == 201
    guest_token = guest_resp.json()["access_token"]
    guest_headers = {"Authorization": f"Bearer {guest_token}"}

    # 3. Create Order as the guest (cash: this test covers order totals/state machine,
    # not payment initiation -- non-cash orders start PENDING_PAYMENT, see test_payments.py)
    order_payload = {
        "outlet_id": outlet_id,
        "items": [
            {"menu_item_id": item_id, "quantity": 2}  # 2 * $500.00 = $1000.00
        ],
        "payment_method": "cash",
    }
    order_resp = await async_client.post(f"{settings.API_V1_STR}/orders/", json=order_payload, headers=guest_headers)
    assert order_resp.status_code == 201
    order_data = order_resp.json()

    order_id = order_data["id"]
    assert order_data["status"] == OrderStatus.CREATED.value
    assert order_data["total_usd_cents"] == 100000  # Backend calculated it correctly

    # 4. Test Invalid State Transition (CREATED -> DELIVERED should fail) as staff
    invalid_patch = await async_client.patch(
        f"{settings.API_V1_STR}/orders/{order_id}/status",
        json={"status": OrderStatus.DELIVERED.value},
        headers=staff_headers
    )
    assert invalid_patch.status_code == 400
    assert "Invalid state transition" in invalid_patch.json()["detail"]

    # 5. Test Valid State Transition (CREATED -> PENDING_PAYMENT should succeed)
    valid_patch = await async_client.patch(
        f"{settings.API_V1_STR}/orders/{order_id}/status",
        json={"status": OrderStatus.PENDING_PAYMENT.value},
        headers=staff_headers
    )
    assert valid_patch.status_code == 200
    assert valid_patch.json()["status"] == OrderStatus.PENDING_PAYMENT.value
