import uuid
from math import ceil
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from app.models.enums import OrderStatus, OrderType, PaymentMethod, PaymentEntityType, PaymentStatus, UserRole
from app.models.customer import Guest
from app.models.menu_item import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.user import User
from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.services.audit_service import write_audit_log
from app.websocket_manager import order_ws_manager

ALLOWED_TRANSITIONS = {
    OrderStatus.CREATED: [OrderStatus.PENDING_PAYMENT, OrderStatus.PAID, OrderStatus.CANCELLED],
    OrderStatus.PENDING_PAYMENT: [OrderStatus.PAID, OrderStatus.PAYMENT_FAILED, OrderStatus.EXPIRED, OrderStatus.CANCELLED],
    OrderStatus.PAID: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
    OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
    OrderStatus.READY: [OrderStatus.DISPATCHED, OrderStatus.DELIVERED],
    OrderStatus.DISPATCHED: [OrderStatus.DELIVERED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: [],
    OrderStatus.PAYMENT_FAILED: [],
    OrderStatus.EXPIRED: [],
}


async def create_order(db: AsyncSession, order_in: OrderCreate, cashier_id: Optional[uuid.UUID] = None, current_user: Optional[User] = None) -> Order:
    outlet_id = order_in.outlet_id
    if current_user and current_user.role != UserRole.owner and current_user.outlet_id:
        outlet_id = current_user.outlet_id

    guest_id = order_in.guest_id
    if guest_id is None and order_in.guest is not None:
        guest_result = await db.execute(select(Guest).where(Guest.phone_number == order_in.guest.phone_number))
        guest = guest_result.scalars().first()
        if not guest:
            guest = Guest(**order_in.guest.model_dump())
            db.add(guest)
            await db.flush()
        guest_id = guest.id
    if guest_id is None:
        raise HTTPException(status_code=400, detail="guest_id or guest details are required")

    db_order = Order(
        outlet_id=outlet_id,
        guest_id=guest_id,
        cashier_id=cashier_id,
        order_type=OrderType.delivery if order_in.is_delivery else order_in.order_type,
        table_number=order_in.table_number,
        room_id=order_in.room_id,
        is_delivery=order_in.is_delivery,
        delivery_address=order_in.delivery_address,
        notes=order_in.notes,
        total_usd_cents=0,
    )
    db.add(db_order)
    await db.flush()

    total_usd_cents = 0
    for item_in in order_in.items:
        result = await db.execute(select(MenuItem).where(MenuItem.id == item_in.menu_item_id, MenuItem.outlet_id == outlet_id))
        menu_item = result.scalars().first()
        if not menu_item or not menu_item.is_available:
            raise HTTPException(status_code=400, detail=f"Menu item {item_in.menu_item_id} is invalid, unavailable, or not in this outlet")
        subtotal = menu_item.price_usd_cents * item_in.quantity
        total_usd_cents += subtotal
        db.add(OrderItem(
            order_id=db_order.id,
            menu_item_id=menu_item.id,
            quantity=item_in.quantity,
            unit_price_usd_cents=menu_item.price_usd_cents,
            subtotal_usd_cents=subtotal,
            special_instructions=item_in.special_instructions,
        ))

    db_order.total_usd_cents = total_usd_cents
    if order_in.payment_method == PaymentMethod.cash:
        db_order.status = OrderStatus.CREATED
        db.add(Payment(entity_type=PaymentEntityType.order, entity_id=db_order.id, amount_usd_cents=total_usd_cents, method=PaymentMethod.cash, status=PaymentStatus.pending))
    else:
        db_order.status = OrderStatus.PENDING_PAYMENT
    await db.commit()
    return await get_order(db, db_order.id)


async def get_order(db: AsyncSession, order_id: uuid.UUID) -> Order | None:
    result = await db.execute(select(Order).options(selectinload(Order.items)).where(Order.id == order_id))
    return result.scalars().first()


async def get_orders(db: AsyncSession, outlet_id: Optional[uuid.UUID] = None, page: int = 1, limit: int = 50) -> tuple[list[Order], int]:
    query = select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc())
    count_query = select(func.count(Order.id))
    if outlet_id:
        query = query.where(Order.outlet_id == outlet_id)
        count_query = count_query.where(Order.outlet_id == outlet_id)
    total = await db.scalar(count_query) or 0
    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    items = list(result.scalars().all())
    return items, total


async def update_order_status(db: AsyncSession, order_id: uuid.UUID, new_status: OrderStatusUpdate) -> Order:
    db_order = await get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    old_status = db_order.status
    target_status = new_status.status
    if target_status not in ALLOWED_TRANSITIONS.get(old_status, []):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid state transition from {old_status.value} to {target_status.value}")
    db_order.status = target_status
    await write_audit_log(db, "order_status_changed", "order", db_order.id, old_value={"status": old_status.value}, new_value={"status": target_status.value})
    await db.commit()
    await db.refresh(db_order)
    await order_ws_manager.broadcast_order_update(db_order.outlet_id, {"type": "order_update", "order_id": str(db_order.id), "status": db_order.status.value, "updated_at": db_order.updated_at.isoformat()})
    return await get_order(db, order_id)
