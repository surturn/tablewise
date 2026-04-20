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
async def create_category(
    category_in: MenuCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles([UserRole.OWNER, UserRole.BRANCH_MANAGER]))
):
    """Create a new menu category (e.g., 'Mains', 'Drinks')."""
    return await menu_service.create_category(db, category_in)

@router.get("/categories", response_model=List[MenuCategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all active menu categories. Public route for the frontend."""
    return await menu_service.get_categories(db)

@router.post("/items", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    item_in: MenuItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles([UserRole.OWNER, UserRole.BRANCH_MANAGER]))
):
    """Create a new menu item and assign it to a category."""
    return await menu_service.create_item(db, item_in)

@router.get("/items", response_model=List[MenuItemResponse])
async def list_menu_items(
    category_id: Optional[uuid.UUID] = Query(None, description="Filter items by category ID"),
    db: AsyncSession = Depends(get_db)
):
    """List menu items. Optionally filter by `category_id`. Public route."""
    return await menu_service.get_items(db, category_id)