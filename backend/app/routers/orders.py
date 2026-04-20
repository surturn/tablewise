import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services import order_service
from app.routers.deps import require_roles, get_current_active_user, get_current_user
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
        order_in: OrderCreate,
        db: AsyncSession = Depends(get_db),
        # Optional dependency: If logged in, we check if it's a cashier
        current_user: Optional[User] = Depends(get_current_user)
):
    """
    Create a new order.
    Can be public (customer web ordering) or authenticated (Cashier POS).
    """
    cashier_id = current_user.id if current_user and current_user.role == UserRole.CASHIER else None
    return await order_service.create_order(db, order_in, cashier_id=cashier_id)


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
        branch_id: Optional[uuid.UUID] = Query(None, description="Filter by Branch ID"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(
            require_roles([UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.CASHIER, UserRole.CHEF]))
):
    """List orders. Restricted to staff."""
    query_branch = branch_id
    if current_user.role in [UserRole.BRANCH_MANAGER, UserRole.CASHIER, UserRole.CHEF]:
        query_branch = current_user.branch_id

    return await order_service.get_orders(db, branch_id=query_branch)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve details for a specific order."""
    order = await order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
        order_id: uuid.UUID,
        status_update: OrderStatusUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(
            require_roles([UserRole.OWNER, UserRole.BRANCH_MANAGER, UserRole.CHEF, UserRole.RIDER]))
):
    """
    Update the status of an order. Strict state transitions apply.
    """
    return await order_service.update_order_status(db, order_id, status_update)