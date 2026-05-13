import json
import logging
import uuid
from typing import Any, Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import stripe

from app.config import settings
from app.models.enums import BookingPaymentStatus, BookingStatus, OrderStatus, PaymentEntityType, PaymentMethod, PaymentStatus
from app.models.order import Order
from app.models.payment import Payment
from app.models.rooms import Booking
from app.services.audit_service import write_audit_log
from app.tasks import deduct_inventory, send_email, send_sms_notification

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


async def create_stripe_payment_intent(
    amount_usd_cents: int,
    entity_type: str,
    entity_id: str,
    customer_email: str,
    metadata: dict[str, Any],
) -> stripe.PaymentIntent:
    if amount_usd_cents <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be positive")
    return await stripe.PaymentIntent.create_async(
        amount=amount_usd_cents,
        currency="usd",
        receipt_email=customer_email,
        metadata={"entity_type": entity_type, "entity_id": entity_id, **metadata},
    )


async def create_payment_intent_for_entity(
    db: AsyncSession,
    entity_type: PaymentEntityType,
    entity_id: uuid.UUID,
    customer_email: str,
    metadata: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    amount = await _get_entity_amount(db, entity_type, entity_id)
    intent = await create_stripe_payment_intent(amount, entity_type.value, str(entity_id), customer_email, metadata or {})
    payment = Payment(
        entity_type=entity_type,
        entity_id=entity_id,
        amount_usd_cents=amount,
        method=PaymentMethod.stripe,
        status=PaymentStatus.pending,
        stripe_payment_intent_id=intent.id,
    )
    db.add(payment)
    await db.commit()
    return {"payment_intent_id": intent.id, "client_secret": intent.client_secret, "amount_usd_cents": amount}


async def handle_stripe_webhook(db: AsyncSession, payload: bytes, sig_header: str, ip_address: str | None = None) -> dict:
    try:
        stripe.WebhookSignature.verify_header(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        event = json.loads(payload.decode("utf-8"))
    except (stripe.error.SignatureVerificationError, ValueError) as exc:
        logger.warning("Rejected unverified Stripe webhook: %s", exc)
        await write_audit_log(
            db,
            action="stripe_webhook_signature_failed",
            entity_type="payment_webhook",
            new_value={"error": str(exc)},
            ip_address=ip_address,
        )
        await db.commit()
        raise HTTPException(status_code=400, detail="Invalid webhook signature") from exc

    event_type = event.get("type")
    payment_intent = event.get("data", {}).get("object", {})
    if event_type == "payment_intent.succeeded":
        await handle_payment_success(db, payment_intent)
    elif event_type == "payment_intent.payment_failed":
        await handle_payment_failure(db, payment_intent)
    return {"received": True}


async def handle_payment_success(db: AsyncSession, payment_intent: dict[str, Any]) -> None:
    metadata = payment_intent.get("metadata") or {}
    entity_type = PaymentEntityType(metadata.get("entity_type"))
    entity_id = uuid.UUID(metadata.get("entity_id"))
    payment = await _get_payment(db, payment_intent.get("id"), entity_type, entity_id)
    if payment and payment.status == PaymentStatus.success:
        return

    charge = _latest_charge(payment_intent)
    if payment is None:
        payment = Payment(
            entity_type=entity_type,
            entity_id=entity_id,
            amount_usd_cents=int(payment_intent["amount"]),
            method=PaymentMethod.stripe,
            stripe_payment_intent_id=payment_intent.get("id"),
        )
        db.add(payment)
    payment.status = PaymentStatus.success
    payment.stripe_charge_id = charge.get("id") if charge else None
    payment.receipt_url = charge.get("receipt_url") if charge else None

    if entity_type == PaymentEntityType.order:
        order = await db.get(Order, entity_id)
        if order:
            order.status = OrderStatus.PAID
            deduct_inventory.delay(str(order.id))
            await write_audit_log(db, "order_paid", "order", order.id, new_value={"status": order.status.value})
    else:
        booking = await db.get(Booking, entity_id)
        if booking:
            booking.status = BookingStatus.confirmed
            booking.payment_status = BookingPaymentStatus.paid
            booking.stripe_payment_intent_id = payment_intent.get("id")
            send_email.delay(str(booking.id), "booking_confirmation")
            await write_audit_log(db, "booking_confirmed", "booking", booking.id, new_value={"status": booking.status.value})
    await db.commit()


async def handle_payment_failure(db: AsyncSession, payment_intent: dict[str, Any]) -> None:
    metadata = payment_intent.get("metadata") or {}
    entity_type = PaymentEntityType(metadata.get("entity_type"))
    entity_id = uuid.UUID(metadata.get("entity_id"))
    payment = await _get_payment(db, payment_intent.get("id"), entity_type, entity_id)
    if payment:
        payment.status = PaymentStatus.failed
    if entity_type == PaymentEntityType.order:
        order = await db.get(Order, entity_id)
        if order:
            order.status = OrderStatus.PAYMENT_FAILED
    await write_audit_log(db, "payment_failed", entity_type.value, entity_id, new_value={"stripe_payment_intent_id": payment_intent.get("id")})
    await db.commit()


async def mark_paid_cash(db: AsyncSession, entity_type: PaymentEntityType, entity_id: uuid.UUID, user_id: uuid.UUID) -> Payment:
    amount = await _get_entity_amount(db, entity_type, entity_id)
    payment = Payment(entity_type=entity_type, entity_id=entity_id, amount_usd_cents=amount, method=PaymentMethod.cash, status=PaymentStatus.success)
    db.add(payment)
    if entity_type == PaymentEntityType.order:
        order = await db.get(Order, entity_id)
        if order:
            order.status = OrderStatus.PAID
            deduct_inventory.delay(str(order.id))
    else:
        booking = await db.get(Booking, entity_id)
        if booking:
            booking.status = BookingStatus.confirmed
            booking.payment_status = BookingPaymentStatus.paid
    await write_audit_log(db, "cash_payment_marked_paid", entity_type.value, entity_id, user_id=user_id, new_value={"amount_usd_cents": amount})
    await db.commit()
    await db.refresh(payment)
    return payment


async def _get_entity_amount(db: AsyncSession, entity_type: PaymentEntityType, entity_id: uuid.UUID) -> int:
    entity = await db.get(Order if entity_type == PaymentEntityType.order else Booking, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"{entity_type.value} not found")
    return entity.total_usd_cents


async def _get_payment(db: AsyncSession, intent_id: str, entity_type: PaymentEntityType, entity_id: uuid.UUID) -> Payment | None:
    result = await db.execute(select(Payment).where(Payment.stripe_payment_intent_id == intent_id))
    payment = result.scalars().first()
    if payment:
        return payment
    result = await db.execute(select(Payment).where(Payment.entity_type == entity_type, Payment.entity_id == entity_id, Payment.method == PaymentMethod.stripe))
    return result.scalars().first()


def _latest_charge(payment_intent: dict[str, Any]) -> dict[str, Any] | None:
    charges = payment_intent.get("charges", {}).get("data") or []
    return charges[0] if charges else None
