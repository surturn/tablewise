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

    # 1. Create a Category
    cat_payload = {"name": "Mains", "description": "Main courses"}
    cat_resp = await async_client.post(f"{settings.API_V1_STR}/menu/categories", json=cat_payload, headers=headers)
    assert cat_resp.status_code == 201
    category_id = cat_resp.json()["id"]

    # 2. Create a Menu Item
    item_payload = {
        "name": "Nyama Choma",
        "description": "Grilled goat meat",
        "price": 1200.00,
        "category_id": category_id
    }
    item_resp = await async_client.post(f"{settings.API_V1_STR}/menu/items", json=item_payload, headers=headers)
    assert item_resp.status_code == 201
    assert item_resp.json()["name"] == "Nyama Choma"

    # 3. List Menu Items (Public)
    list_resp = await async_client.get(f"{settings.API_V1_STR}/menu/items?category_id={category_id}")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) > 0
    assert items[0]["name"] == "Nyama Choma"