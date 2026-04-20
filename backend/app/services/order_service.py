import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu_item import MenuItem
from app.models.enums import OrderStatus
from app.schemas.order import OrderCreate, OrderStatusUpdate

# Strict State Machine Definition
ALLOWED_TRANSITIONS = {
    OrderStatus.CREATED: [OrderStatus.PENDING_PAYMENT, OrderStatus.CANCELLED],
    OrderStatus.PENDING_PAYMENT: [OrderStatus.PAID, OrderStatus.PAYMENT_FAILED, OrderStatus.EXPIRED,
                                  OrderStatus.CANCELLED],
    OrderStatus.PAID: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
    OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
    OrderStatus.READY: [OrderStatus.DISPATCHED, OrderStatus.DELIVERED],
    OrderStatus.DISPATCHED: [OrderStatus.DELIVERED],
    # Terminal states have no outward transitions
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: [],
    OrderStatus.PAYMENT_FAILED: [],
    OrderStatus.EXPIRED: []
}


async def create_order(db: AsyncSession, order_in: OrderCreate, cashier_id: Optional[uuid.UUID] = None) -> Order:
    # 1. Initialize Order
    db_order = Order(
        branch_id=order_in.branch_id,
        customer_id=order_in.customer_id,
        cashier_id=cashier_id,
        is_delivery=order_in.is_delivery,
        delivery_address=order_in.delivery_address,
        notes=order_in.notes,
        total_amount=0.0  # Will calculate dynamically
    )
    db.add(db_order)
    await db.flush()  # Flush to get db_order.id

    total_amount = 0.0

    # 2. Process Items and Calculate Totals safely on the backend
    for item_in in order_in.items:
        # Fetch actual menu item to get the secure price
        result = await db.execute(select(MenuItem).where(MenuItem.id == item_in.menu_item_id))
        menu_item = result.scalars().first()

        if not menu_item or not menu_item.is_active:
            raise HTTPException(status_code=400, detail=f"Menu item {item_in.menu_item_id} is invalid or inactive")

        subtotal = float(menu_item.price) * item_in.quantity
        total_amount += subtotal

        db_order_item = OrderItem(
            order_id=db_order.id,
            menu_item_id=menu_item.id,
            quantity=item_in.quantity,
            unit_price=float(menu_item.price),
            subtotal=subtotal,
            special_instructions=item_in.special_instructions
        )
        db.add(db_order_item)

    db_order.total_amount = total_amount
    await db.commit()

    # Refresh and load relationships for the response
    return await get_order(db, db_order.id)


async def get_order(db: AsyncSession, order_id: uuid.UUID) -> Order | None:
    # selectinload ensures the related items are eagerly loaded to avoid LazyLoad errors in async context
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    return result.scalars().first()


async def get_orders(db: AsyncSession, branch_id: Optional[uuid.UUID] = None) -> List[Order]:
    query = select(Order).options(selectinload(Order.items))
    if branch_id:
        query = query.where(Order.branch_id == branch_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_order_status(db: AsyncSession, order_id: uuid.UUID, new_status: OrderStatusUpdate) -> Order:
    db_order = await get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    current_status = db_order.status
    target_status = new_status.status

    if target_status not in ALLOWED_TRANSITIONS.get(current_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid state transition from {current_status.value} to {target_status.value}"
        )

    db_order.status = target_status
    await db.commit()
    await db.refresh(db_order)
    return db_order