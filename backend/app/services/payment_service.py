import uuid
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import BookingPaymentStatus, BookingStatus, OrderStatus, PaymentEntityType, PaymentMethod, PaymentStatus
from app.models.order import Order
from app.models.payment import Payment
from app.models.rooms import Booking
from app.services import mpesa_service
from app.services.audit_service import write_audit_log
from app.tasks import deduct_inventory, send_email


async def create_payment_intent_for_entity(
    db: AsyncSession,
    entity_type: PaymentEntityType,
    entity_id: uuid.UUID,
    phone_number: str,
    metadata: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    amount = await _get_entity_amount(db, entity_type, entity_id)
    return await mpesa_service.initiate_stk_push(db, phone_number, amount, entity_type, entity_id)


async def handle_payment_success(db: AsyncSession, payment: Payment, mpesa_receipt_number: Optional[str] = None) -> None:
    if payment.status == PaymentStatus.success:
        return

    payment.status = PaymentStatus.success
    payment.mpesa_receipt_number = mpesa_receipt_number

    if payment.entity_type == PaymentEntityType.order:
        order = await db.get(Order, payment.entity_id)
        if order:
            order.status = OrderStatus.PAID
            deduct_inventory.delay(str(order.id))
            await write_audit_log(db, "order_paid", "order", order.id, new_value={"status": order.status.value})
    else:
        booking = await db.get(Booking, payment.entity_id)
        if booking:
            booking.status = BookingStatus.confirmed
            booking.payment_status = BookingPaymentStatus.paid
            booking.mpesa_checkout_request_id = payment.mpesa_checkout_request_id
            send_email.delay(str(booking.id), "booking_confirmation")
            await write_audit_log(db, "booking_confirmed", "booking", booking.id, new_value={"status": booking.status.value})
    await db.commit()


async def handle_payment_failure(db: AsyncSession, payment: Payment, reason: Optional[str] = None) -> None:
    payment.status = PaymentStatus.failed
    if payment.entity_type == PaymentEntityType.order:
        order = await db.get(Order, payment.entity_id)
        if order:
            order.status = OrderStatus.PAYMENT_FAILED
    await write_audit_log(
        db,
        "payment_failed",
        payment.entity_type.value,
        payment.entity_id,
        new_value={"mpesa_checkout_request_id": payment.mpesa_checkout_request_id, "reason": reason},
    )
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
