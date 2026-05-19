import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.menu import MenuCategoryCreate, MenuCategoryResponse, MenuItemCreate, MenuItemResponse
from app.services import menu_service
from app.routers.deps import require_roles
from app.models.enums import UserRole

router = APIRouter()


@router.post("/categories", response_model=MenuCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_in: MenuCategoryCreate, db: AsyncSession = Depends(get_db), current_user=Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.restaurant_manager]))):
    return await menu_service.create_category(db, category_in)


@router.get("/categories", response_model=List[MenuCategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    return await menu_service.get_categories(db)


@router.post("/items", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(item_in: MenuItemCreate, db: AsyncSession = Depends(get_db), current_user=Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.restaurant_manager, UserRole.bartender]))):
    return await menu_service.create_item(db, item_in)


@router.get("/items", response_model=List[MenuItemResponse])
async def list_menu_items(
    outlet_id: uuid.UUID = Query(..., description="Required outlet ID used to scope menu pricing and availability"),
    category_id: Optional[uuid.UUID] = Query(None, description="Filter items by category ID"),
    db: AsyncSession = Depends(get_db),
):
    return await menu_service.get_items(db, outlet_id=outlet_id, category_id=category_id)
