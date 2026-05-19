import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import BaseModelMixin
from app.models.enums import PaymentStatus, PaymentMethod

class Payment(Base, BaseModelMixin):
    __tablename__ = "payments"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"), unique=True, index=True
    )
    
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(SQLEnum(PaymentMethod), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Idempotency and tracing for Stripe, mobile-money aggregators, and legacy M-Pesa callbacks
    checkout_request_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    mpesa_receipt_number: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    payer_phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    stripe_checkout_session_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    mobile_money_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    external_reference: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="payment")