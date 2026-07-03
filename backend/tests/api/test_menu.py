import pytest
from httpx import AsyncClient
from app.models.user import User
from app.config import settings
from app.utils.jwt import create_access_token


@pytest.mark.asyncio
async def test_create_and_list_menu(async_client: AsyncClient, test_owner: User):
    """Integration test: Verify Owner can create categories/items, and public can view them."""
    token = create_access_token(subject=str(test_owner.id), role=test_owner.role)
    headers = {"Authorization": f"Bearer {token}"}

    # 0. Create an Outlet (menu items are scoped to an outlet)
    branch_payload = {"name": "Test Outlet", "location": "Test", "contact_number": "0700000000"}
    branch_resp = await async_client.post(f"{settings.API_V1_STR}/branches/", json=branch_payload, headers=headers)
    assert branch_resp.status_code == 201
    outlet_id = branch_resp.json()["id"]

    # 1. Create a Category
    cat_payload = {"name": "Mains", "description": "Main courses"}
    cat_resp = await async_client.post(f"{settings.API_V1_STR}/menu/categories", json=cat_payload, headers=headers)
    assert cat_resp.status_code == 201
    category_id = cat_resp.json()["id"]

    # 2. Create a Menu Item (schema requires price_usd_cents and outlet_id, not price)
    item_payload = {
        "name": "Nyama Choma",
        "description": "Grilled goat meat",
        "price_usd_cents": 120000,
        "category_id": category_id,
        "outlet_id": outlet_id,
    }
    item_resp = await async_client.post(f"{settings.API_V1_STR}/menu/items", json=item_payload, headers=headers)
    assert item_resp.status_code == 201
    assert item_resp.json()["name"] == "Nyama Choma"

    # 3. List Menu Items (Public, but outlet_id is required to scope pricing/availability)
    list_resp = await async_client.get(f"{settings.API_V1_STR}/menu/items?outlet_id={outlet_id}&category_id={category_id}")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) > 0
    assert items[0]["name"] == "Nyama Choma"
