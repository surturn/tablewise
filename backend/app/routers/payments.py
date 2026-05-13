import uuid
from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.enums import PaymentEntityType, UserRole
from app.models.user import User
from app.routers.deps import require_roles
from app.schemas.payment import CashMarkPaidResponse, PaymentIntentRequest, PaymentIntentResponse
from app.services import payment_service

router = APIRouter()


@router.post("/payment-intent", response_model=PaymentIntentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_intent(request: PaymentIntentRequest, db: AsyncSession = Depends(get_db)):
    return await payment_service.create_payment_intent_for_entity(db, request.entity_type, request.entity_id, request.customer_email, request.metadata)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request, stripe_signature: str = Header(..., alias="Stripe-Signature"), db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    return await payment_service.handle_stripe_webhook(db, payload, stripe_signature, request.client.host if request.client else None)


@router.post("/{entity_type}/{entity_id}/mark-paid-cash", response_model=CashMarkPaidResponse)
async def mark_paid_cash(entity_type: PaymentEntityType, entity_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_roles([UserRole.owner, UserRole.receptionist]))):
    payment = await payment_service.mark_paid_cash(db, entity_type, entity_id, current_user.id)
    return {"entity_id": entity_id, "entity_type": entity_type, "status": payment.status, "method": payment.method, "audit_logged": True}
