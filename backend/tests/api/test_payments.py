import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models import Outlet, Guest
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app.models.enums import OrderStatus, PaymentStatus, PaymentMethod
from app.utils.jwt import create_access_token


async def _setup_order(db_session: AsyncSession) -> Order:
    outlet = Outlet(name="Payments Test Outlet", location="Nairobi", contact_number="0700000000")
    guest = Guest(phone_number="0700111222", full_name="Payments Test Guest")
    db_session.add_all([outlet, guest])
    await db_session.flush()

    order = Order(outlet_id=outlet.id, guest_id=guest.id, total_usd_cents=10000, status=OrderStatus.PENDING_PAYMENT)
    db_session.add(order)
    await db_session.flush()
    await db_session.commit()
    return order


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
    assert data["amount_usd_cents"] == 10000

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
        amount_usd_cents=10000,
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
        amount_usd_cents=10000,
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
        amount_usd_cents=10000,  # expected KES 100
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
        amount_usd_cents=10000,
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
