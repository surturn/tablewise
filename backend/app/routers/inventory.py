import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.inventory import InventoryItemCreate, InventoryItemResponse, InventoryItemUpdate
from app.services import inventory_service
from app.routers.deps import require_roles
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(item_in: InventoryItemCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.restaurant_manager, UserRole.bartender]))):
    if current_user.role not in [UserRole.owner, UserRole.hotel_manager] and item_in.outlet_id != current_user.outlet_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create inventory for another outlet")
    return await inventory_service.create_item(db, item_in)


@router.get("/", response_model=PaginatedResponse[InventoryItemResponse])
async def list_inventory(outlet_id: Optional[uuid.UUID] = Query(None), page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.restaurant_manager, UserRole.bartender]))):
    query_outlet = outlet_id
    if current_user.role not in [UserRole.owner, UserRole.hotel_manager]:
        query_outlet = current_user.outlet_id
    return await inventory_service.get_items(db, outlet_id=query_outlet, page=page, limit=limit)


@router.patch("/{item_id}/stock", response_model=InventoryItemResponse)
async def adjust_stock(item_id: uuid.UUID, update_data: InventoryItemUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.restaurant_manager, UserRole.bartender]))):
    item = await inventory_service.update_stock(db, item_id, update_data, current_user.id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return item
