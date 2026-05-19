import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.menu_category import MenuCategory
from app.models.menu_item import MenuItem
from app.schemas.menu import MenuCategoryCreate, MenuItemCreate


async def create_category(db: AsyncSession, category_in: MenuCategoryCreate) -> MenuCategory:
    db_obj = MenuCategory(**category_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_categories(db: AsyncSession) -> List[MenuCategory]:
    result = await db.execute(select(MenuCategory).where(MenuCategory.is_active.is_(True)))
    return list(result.scalars().all())


async def create_item(db: AsyncSession, item_in: MenuItemCreate) -> MenuItem:
    db_obj = MenuItem(**item_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_items(db: AsyncSession, outlet_id: uuid.UUID, category_id: Optional[uuid.UUID] = None) -> List[MenuItem]:
    query = select(MenuItem).where(MenuItem.outlet_id == outlet_id, MenuItem.is_available.is_(True))
    if category_id:
        query = query.where(MenuItem.category_id == category_id)
    result = await db.execute(query)
    return list(result.scalars().all())
