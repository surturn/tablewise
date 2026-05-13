import uuid
from math import ceil
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.models.inventory_item import InventoryItem
from app.models.operations import StockMovement
from app.schemas.common import PaginatedResponse
from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate


async def create_item(db: AsyncSession, item_in: InventoryItemCreate) -> InventoryItem:
    db_obj = InventoryItem(**item_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_items(db: AsyncSession, outlet_id: Optional[uuid.UUID] = None, page: int = 1, limit: int = 50) -> PaginatedResponse[InventoryItem]:
    query = select(InventoryItem).order_by(InventoryItem.name)
    count_query = select(func.count(InventoryItem.id))
    if outlet_id:
        query = query.where(InventoryItem.outlet_id == outlet_id)
        count_query = count_query.where(InventoryItem.outlet_id == outlet_id)
    total = await db.scalar(count_query) or 0
    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    return PaginatedResponse(items=list(result.scalars().all()), total=total, page=page, pages=ceil(total / limit) if total else 0)


async def update_stock(db: AsyncSession, item_id: uuid.UUID, update_data: InventoryItemUpdate, user_id: uuid.UUID | None = None) -> InventoryItem | None:
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id).with_for_update())
    item = result.scalars().first()
    if not item:
        return None
    item.quantity = float(item.quantity) + update_data.quantity_added
    db.add(StockMovement(inventory_item_id=item.id, change_quantity=int(update_data.quantity_added), reason=update_data.reason, user_id=user_id))
    await db.commit()
    await db.refresh(item)
    return item
