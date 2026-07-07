from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models import Outlet, Guest, Property, RoomType, Room, Booking
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app.models.enums import BookingPaymentStatus, BookingStatus, OrderStatus, PaymentEntityType, PaymentMethod, PaymentStatus, RoomStatus, UserRole
from app.services import payment_service
from app.utils.jwt import create_access_token


async def _setup_order(db_session: AsyncSession) -> Order:
    outlet = Outlet(name="Payments Test Outlet", location="Nairobi", contact_number="0700000000")
    guest = Guest(phone_number="0700111222", full_name="Payments Test Guest")
    db_session.add_all([outlet, guest])
    await db_session.flush()

    order = Order(outlet_id=outlet.id, guest_id=guest.id, total_kes_cents=10000, status=OrderStatus.PENDING_PAYMENT)
    db_session.add(order)
    await db_session.flush()
    await db_session.commit()
    return order


async def _setup_booking(db_session: AsyncSession) -> Booking:
    property_ = Property(name="Payments Test Property")
    guest = Guest(phone_number="0700333444", full_name="Payments Test Booking Guest")
    db_session.add_all([property_, guest])
    await db_session.flush()

    room_type = RoomType(property_id=property_.id, name="Standard", capacity=2, base_price_kes_cents=850000)
    db_session.add(room_type)
    await db_session.flush()

    room = Room(room_type_id=room_type.id, room_number="101", floor=1, status=RoomStatus.available)
    db_session.add(room)
    await db_session.flush()

    booking = Booking(
        room_id=room.id,
        guest_id=guest.id,
        check_in=date.today(),
        check_out=date.today() + timedelta(days=2),
        status=BookingStatus.pending,
        payment_status=BookingPaymentStatus.unpaid,
        total_kes_cents=1700000,
    )
    db_session.add(booking)
    await db_session.flush()
    await db_session.commit()
    return booking


@pytest.mark.asyncio
async def test_handle_payment_success_and_failure_are_symmetric_across_entity_types(db_session: AsyncSession):
    """Regression test: handle_payment_success/handle_payment_failure must both update Order and
    Booking correctly. A prior version of handle_payment_failure only updated Order, silently
    leaving a failed booking payment as 'unpaid' -- indistinguishable from never attempted.
    See docs/payment-currency-and-booking-prd.md FR-7/FR-8.
    """
    success_order = await _setup_order(db_session)
    success_payment = Payment(entity_type=PaymentEntityType.order, entity_id=success_order.id, amount_kes_cents=10000, method=PaymentMethod.mpesa, status=PaymentStatus.pending)
    db_session.add(success_payment)
    await db_session.commit()
    await payment_service.handle_payment_success(db_session, success_payment, mpesa_receipt_number="R1")
    await db_session.refresh(success_order)
    assert success_order.status == OrderStatus.PAID

    success_booking = await _setup_booking(db_session)
    success_booking_payment = Payment(entity_type=PaymentEntityType.booking, entity_id=success_booking.id, amount_kes_cents=1700000, method=PaymentMethod.mpesa, status=PaymentStatus.pending)
    db_session.add(success_booking_payment)
    await db_session.commit()
    await payment_service.handle_payment_success(db_session, success_booking_payment, mpesa_receipt_number="R2")
    await db_session.refresh(success_booking)
    assert success_booking.status == BookingStatus.confirmed
    assert success_booking.payment_status == BookingPaymentStatus.paid

    failed_order = await _setup_order(db_session)
    failed_order_payment = Payment(entity_type=PaymentEntityType.order, entity_id=failed_order.id, amount_kes_cents=10000, method=PaymentMethod.mpesa, status=PaymentStatus.pending)
    db_session.add(failed_order_payment)
    await db_session.commit()
    await payment_service.handle_payment_failure(db_session, failed_order_payment, reason="cancelled")
    await db_session.refresh(failed_order)
    assert failed_order.status == OrderStatus.PAYMENT_FAILED

    failed_booking = await _setup_booking(db_session)
    failed_booking_payment = Payment(entity_type=PaymentEntityType.booking, entity_id=failed_booking.id, amount_kes_cents=1700000, method=PaymentMethod.mpesa, status=PaymentStatus.pending)
    db_session.add(failed_booking_payment)
    await db_session.commit()
    await payment_service.handle_payment_failure(db_session, failed_booking_payment, reason="cancelled")
    await db_session.refresh(failed_booking)
    assert failed_booking.status == BookingStatus.pending
    assert failed_booking.payment_status == BookingPaymentStatus.failed


@pytest.mark.asyncio
async def test_payment_intent_returns_404_for_missing_entity(async_client: AsyncClient, db_session: AsyncSession, test_owner: User):
    """Regression test for FR-11: consolidating the ownership check into payment_service must
    preserve the router's original 404-before-403 behavior for a nonexistent entity."""
    token = create_access_token(subject=str(test_owner.id), role=test_owner.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post(
        f"{settings.API_V1_STR}/payments/payment-intent",
        json={"entity_type": "order", "entity_id": "00000000-0000-0000-0000-000000000000", "phone_number": "0700111222"},
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_payment_intent_returns_403_for_unauthorized_guest(async_client: AsyncClient, db_session: AsyncSession):
    """Regression test for FR-11: a guest who doesn't own the order must still get 403, not 404
    or a silently-succeeded payment intent, after the ownership check moved into payment_service."""
    order = await _setup_order(db_session)
    other_guest = Guest(phone_number="0700999888", full_name="Someone Else")
    db_session.add(other_guest)
    await db_session.commit()
    await db_session.refresh(other_guest)

    token = create_access_token(subject=str(other_guest.id), role=UserRole.customer, account_type="guest")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post(
        f"{settings.API_V1_STR}/payments/payment-intent",
        json={"entity_type": "order", "entity_id": str(order.id), "phone_number": "0700111222"},
        headers=headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_stk_push_initiation_mock_mode(async_client: AsyncClient, db_session: AsyncSession, test_owner: User):
    """Integration test: POST /payments/payment-intent creates a pending M-Pesa Payment in mock mode."""
    order = await _setup_order(db_session)
    token = create_access_token(subject=str(test_owner.id), role=test_owner.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post(
        f"{settings.API_V1_STR}/payments/payment-intent",
        json={"entity_type": "order", "entity_id": str(order.id), "phone_number": "0700111222"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["checkout_request_id"]
    assert data["merchant_request_id"]
    assert data["amount_kes_cents"] == 10000

    result = await db_session.execute(
        Payment.__table__.select().where(Payment.mpesa_checkout_request_id == data["checkout_request_id"])
    )
    payment_row = result.first()
    assert payment_row is not None
    assert payment_row.status == PaymentStatus.pending
    assert payment_row.method == PaymentMethod.mpesa
    assert payment_row.phone_number == "0700111222"


@pytest.mark.asyncio
async def test_mpesa_callback_success(async_client: AsyncClient, db_session: AsyncSession):
    """Integration test: A successful Daraja STK push callback marks the Payment/Order paid."""
    order = await _setup_order(db_session)

    checkout_request_id = "ws_CO_1234567890"
    payment = Payment(
        entity_type="order",
        entity_id=order.id,
        amount_kes_cents=10000,
        method=PaymentMethod.mpesa,
        status=PaymentStatus.pending,
        mpesa_checkout_request_id=checkout_request_id,
        mpesa_merchant_request_id="29115-34620561-1",
        phone_number="0700111222",
    )
    db_session.add(payment)
    await db_session.commit()

    webhook_payload = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620561-1",
                "CheckoutRequestID": checkout_request_id,
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 100},
                        {"Name": "MpesaReceiptNumber", "Value": "NLJ7RT61SV"},
                    ]
                },
            }
        }
    }

    response = await async_client.post(f"{settings.API_V1_STR}/payments/mpesa/callback", json=webhook_payload)
    assert response.status_code == 200
    assert response.json()["ResultCode"] == 0

    await db_session.refresh(payment)
    await db_session.refresh(order)

    assert payment.status == PaymentStatus.success
    assert payment.mpesa_receipt_number == "NLJ7RT61SV"
    assert order.status == OrderStatus.PAID


@pytest.mark.asyncio
async def test_mpesa_callback_failure(async_client: AsyncClient, db_session: AsyncSession):
    """Integration test: A failed/cancelled Daraja STK push callback marks the Payment/Order failed."""
    order = await _setup_order(db_session)

    checkout_request_id = "ws_CO_9999999999"
    payment = Payment(
        entity_type="order",
        entity_id=order.id,
        amount_kes_cents=10000,
        method=PaymentMethod.mpesa,
        status=PaymentStatus.pending,
        mpesa_checkout_request_id=checkout_request_id,
        mpesa_merchant_request_id="29115-34620561-2",
        phone_number="0700111222",
    )
    db_session.add(payment)
    await db_session.commit()

    webhook_payload = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620561-2",
                "CheckoutRequestID": checkout_request_id,
                "ResultCode": 1032,
                "ResultDesc": "Request cancelled by user.",
            }
        }
    }

    response = await async_client.post(f"{settings.API_V1_STR}/payments/mpesa/callback", json=webhook_payload)
    assert response.status_code == 200

    await db_session.refresh(payment)
    await db_session.refresh(order)

    assert payment.status == PaymentStatus.failed
    assert order.status == OrderStatus.PAYMENT_FAILED


@pytest.mark.asyncio
async def test_mpesa_callback_amount_mismatch_left_pending(async_client: AsyncClient, db_session: AsyncSession):
    """A success callback whose Amount disagrees with the stored payment is not applied."""
    order = await _setup_order(db_session)

    checkout_request_id = "ws_CO_amount_mismatch"
    payment = Payment(
        entity_type="order",
        entity_id=order.id,
        amount_kes_cents=10000,  # expected KES 100
        method=PaymentMethod.mpesa,
        status=PaymentStatus.pending,
        mpesa_checkout_request_id=checkout_request_id,
        mpesa_merchant_request_id="29115-34620561-3",
        phone_number="0700111222",
    )
    db_session.add(payment)
    await db_session.commit()

    webhook_payload = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620561-3",
                "CheckoutRequestID": checkout_request_id,
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 1},  # attacker/glitch sends KES 1 instead of 100
                        {"Name": "MpesaReceiptNumber", "Value": "FORGED123"},
                    ]
                },
            }
        }
    }

    response = await async_client.post(f"{settings.API_V1_STR}/payments/mpesa/callback", json=webhook_payload)
    assert response.status_code == 200
    assert response.json()["ResultCode"] == 0  # still ack Safaricom to avoid retries

    await db_session.refresh(payment)
    await db_session.refresh(order)

    assert payment.status == PaymentStatus.pending
    assert payment.mpesa_receipt_number is None
    assert order.status == OrderStatus.PENDING_PAYMENT


@pytest.mark.asyncio
async def test_mpesa_late_failure_callback_does_not_override_success(async_client: AsyncClient, db_session: AsyncSession):
    """A duplicate/late failure callback must not downgrade an already-successful payment."""
    order = await _setup_order(db_session)

    checkout_request_id = "ws_CO_late_failure"
    payment = Payment(
        entity_type="order",
        entity_id=order.id,
        amount_kes_cents=10000,
        method=PaymentMethod.mpesa,
        status=PaymentStatus.success,
        mpesa_checkout_request_id=checkout_request_id,
        mpesa_merchant_request_id="29115-34620561-4",
        mpesa_receipt_number="REAL_RECEIPT",
        phone_number="0700111222",
    )
    db_session.add(payment)
    order.status = OrderStatus.PAID
    await db_session.commit()

    webhook_payload = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620561-4",
                "CheckoutRequestID": checkout_request_id,
                "ResultCode": 1032,
                "ResultDesc": "Request cancelled by user.",
            }
        }
    }

    response = await async_client.post(f"{settings.API_V1_STR}/payments/mpesa/callback", json=webhook_payload)
    assert response.status_code == 200

    await db_session.refresh(payment)
    await db_session.refresh(order)

    assert payment.status == PaymentStatus.success
    assert order.status == OrderStatus.PAID
