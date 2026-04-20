import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.inventory import InventoryItemCreate, InventoryItemResponse, InventoryItemUpdate
from app.services import inventory_service
from app.routers.deps import require_roles, get_current_active_user
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
        item_in: InventoryItemCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_roles([UserRole.OWNER, UserRole.BRANCH_MANAGER]))
):
    """
    Create a new inventory item.
    Branch Managers can only create items for their own branch.
    """
    if current_user.role == UserRole.BRANCH_MANAGER and item_in.branch_id != current_user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create inventory for another branch")

    return await inventory_service.create_item(db, item_in)


@router.get("/", response_model=List[InventoryItemResponse])
async def list_inventory(
        branch_id: Optional[uuid.UUID] = Query(None, description="Filter by Branch ID"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_roles([UserRole.OWNER, UserRole.BRANCH_MANAGER]))
):
    """
    List inventory items.
    Branch Managers can only view their own branch's inventory.
    """
    query_branch = branch_id
    if current_user.role == UserRole.BRANCH_MANAGER:
        query_branch = current_user.branch_id

    return await inventory_service.get_items(db, branch_id=query_branch)


@router.patch("/{item_id}/stock", response_model=InventoryItemResponse)
async def adjust_stock(
        item_id: uuid.UUID,
        update_data: InventoryItemUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_roles([UserRole.OWNER, UserRole.BRANCH_MANAGER]))
):
    """Manually adjust stock levels (e.g., received new stock, or logging waste)."""
    item = await inventory_service.update_stock(db, item_id, update_data)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    # Note: A real production system would also create an Audit Log entry here.
    return item