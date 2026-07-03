import uuid
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.enums import PaymentEntityType, UserRole
from app.models.user import User
from app.routers.deps import require_roles, get_current_user_or_customer
from app.models.customer import Guest
from typing import Union
from app.schemas.payment import CashMarkPaidResponse, PaymentIntentRequest, PaymentIntentResponse
from app.services import mpesa_service, payment_service

router = APIRouter()


@router.post("/payment-intent", response_model=PaymentIntentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_intent(
    request: PaymentIntentRequest, 
    db: AsyncSession = Depends(get_db),
    current_account: Union[User, Guest] = Depends(get_current_user_or_customer)
):
    from fastapi import HTTPException
    
    if request.entity_type == PaymentEntityType.order:
        from app.models.order import Order
        entity = await db.get(Order, request.entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Order not found")
        if isinstance(current_account, Guest) and entity.customer_id != current_account.id:
            raise HTTPException(status_code=403, detail="Not authorized to pay for this order")
            
    elif request.entity_type == PaymentEntityType.booking:
        from app.models.rooms import Booking
        entity = await db.get(Booking, request.entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Booking not found")
        if isinstance(current_account, Guest) and entity.guest_id != current_account.id:
            raise HTTPException(status_code=403, detail="Not authorized to pay for this booking")

    return await payment_service.create_payment_intent_for_entity(db, request.entity_type, request.entity_id, request.phone_number, request.metadata)



@router.post("/mpesa/callback", status_code=status.HTTP_200_OK)
async def mpesa_callback(request: Request, db: AsyncSession = Depends(get_db)):
    # Safaricom doesn't sign callbacks the way Stripe does; the callback URL's
    # obscurity is the current trust boundary. IP allowlisting Safaricom's
    # ranges is a follow-up hardening step, not yet implemented.
    payload = await request.json()
    return await mpesa_service.handle_mpesa_callback(db, payload)


@router.post("/{entity_type}/{entity_id}/mark-paid-cash", response_model=CashMarkPaidResponse)
async def mark_paid_cash(entity_type: PaymentEntityType, entity_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.receptionist]))):
    payment = await payment_service.mark_paid_cash(db, entity_type, entity_id, current_user.id)
    return {"entity_id": entity_id, "entity_type": entity_type, "status": payment.status, "method": payment.method, "audit_logged": True}
