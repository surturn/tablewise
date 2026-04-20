import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.inventory_item import InventoryItem
from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate


async def create_item(db: AsyncSession, item_in: InventoryItemCreate) -> InventoryItem:
    db_obj = InventoryItem(**item_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_items(db: AsyncSession, branch_id: Optional[uuid.UUID] = None) -> List[InventoryItem]:
    query = select(InventoryItem)
    if branch_id:
        query = query.where(InventoryItem.branch_id == branch_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_stock(db: AsyncSession, item_id: uuid.UUID, update_data: InventoryItemUpdate) -> InventoryItem | None:
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    item = result.scalars().first()

    if not item:
        return None

    # Apply the stock adjustment
    item.quantity = float(item.quantity) + update_data.quantity_added
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item