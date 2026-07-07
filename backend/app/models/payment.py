import uuid
from typing import Optional
from sqlalchemy import String, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.base import BaseModelMixin
from app.models.enums import PaymentEntityType, PaymentMethod, PaymentStatus


class Payment(Base, BaseModelMixin):
    __tablename__ = "payments"

    entity_type: Mapped[PaymentEntityType] = mapped_column(SQLEnum(PaymentEntityType), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    amount_kes_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(SQLEnum(PaymentMethod), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), default=PaymentStatus.pending, index=True)
    mpesa_checkout_request_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    mpesa_merchant_request_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mpesa_receipt_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    @property
    def order_id(self) -> Optional[uuid.UUID]:
        return self.entity_id if self.entity_type == PaymentEntityType.order else None

    @property
    def amount(self) -> float:
        return self.amount_kes_cents / 100

    @amount.setter
    def amount(self, value: float) -> None:
        self.amount_kes_cents = int(round(float(value) * 100))
