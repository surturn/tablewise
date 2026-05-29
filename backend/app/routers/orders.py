import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from app.database import get_db, AsyncSessionLocal
from app.config import settings
from app.schemas.common import PaginatedResponse, paginate_response
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services import order_service
from app.routers.deps import require_roles, get_optional_current_user
from app.models.enums import UserRole
from app.models.user import User
from app.models.order import Order
from app.websocket_manager import order_ws_manager

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_in: OrderCreate, db: AsyncSession = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    staff_roles = {UserRole.hotel_manager, UserRole.restaurant_manager, UserRole.receptionist, UserRole.chef, UserRole.bartender, UserRole.waiter, UserRole.rider}
    cashier_id = current_user.id if current_user and current_user.role in staff_roles else None
    return await order_service.create_order(db, order_in, cashier_id=cashier_id, current_user=current_user)


@router.get("/", response_model=PaginatedResponse[OrderResponse])
async def list_orders(
    outlet_id: Optional[uuid.UUID] = Query(None, description="Filter by Outlet ID"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.restaurant_manager, UserRole.receptionist, UserRole.chef, UserRole.bartender, UserRole.waiter, UserRole.rider])),
):
    query_outlet = outlet_id
    if current_user.role != UserRole.owner and current_user.outlet_id:
        query_outlet = current_user.outlet_id
    items, total = await order_service.get_orders(db, outlet_id=query_outlet, page=page, limit=limit)
    return paginate_response(items, total, page, limit)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    order = await order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: uuid.UUID, status_update: OrderStatusUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.hotel_manager, UserRole.restaurant_manager, UserRole.receptionist, UserRole.chef, UserRole.bartender, UserRole.waiter, UserRole.rider]))):
    return await order_service.update_order_status(db, order_id, status_update)


@router.websocket("/ws/orders/{outlet_id}")
async def orders_websocket(
    websocket: WebSocket,
    outlet_id: uuid.UUID,
    token: Optional[str] = Query(None)
):
    client_ip = websocket.client.host if websocket.client else "unknown"
    
    # 1. IP Connection Limiting (Max 10)
    if not order_ws_manager.check_ip_limit(client_ip, limit=10):
        await websocket.close(code=4001, reason="Too many concurrent connections from this IP")
        return

    # 2. Extract Token
    if not token:
        await websocket.close(code=4001, reason="Authentication token missing")
        return

    # 3. Validate JWT via python-jose
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        role_str: str = payload.get("role")
        token_outlet_id: Optional[str] = payload.get("outlet_id")
        
        if not user_id_str or not role_str:
            raise JWTError("Missing required claims")
    except JWTError:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    # 4. Strict Authorization Rules
    is_authorized = False
    
    if role_str == UserRole.customer.value:
        # Customer: Must have at least one active order at this outlet
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Order).where(
                    Order.customer_id == uuid.UUID(user_id_str),
                    Order.outlet_id == outlet_id,
                    Order.status.not_in(['delivered', 'payment_failed', 'expired', 'cancelled'])
                ).limit(1)
            )
            if result.scalars().first():
                is_authorized = True
    else:
        # Staff: Must be an allowed role + scoped to this outlet
        allowed_roles = {
            UserRole.chef.value, 
            UserRole.restaurant_manager.value, 
            UserRole.owner.value,
            "kitchen_display"
        }
        if role_str in allowed_roles:
            if role_str == UserRole.owner.value or token_outlet_id == str(outlet_id):
                is_authorized = True

    if not is_authorized:
        await websocket.close(code=4001, reason="Unauthorized access for this outlet")
        return

    # 5. Connect and Manage WebSocket
    await websocket.accept()
    order_ws_manager.connect(outlet_id, websocket, client_ip)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        order_ws_manager.disconnect(outlet_id, websocket, client_ip)
