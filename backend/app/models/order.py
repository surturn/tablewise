import uuid
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Integer, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import BaseModelMixin
from app.models.enums import OrderStatus, OrderType


class Order(Base, BaseModelMixin):
    __tablename__ = "orders"

    outlet_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("outlets.id", ondelete="RESTRICT"), index=True)
    guest_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("guests.id", ondelete="RESTRICT"), index=True)
    cashier_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.CREATED, index=True)
    total_usd_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    order_type: Mapped[OrderType] = mapped_column(SQLEnum(OrderType), default=OrderType.takeaway, index=True)
    table_number: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    room_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True, index=True)
    is_delivery: Mapped[bool] = mapped_column(Boolean, default=False)
    delivery_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    outlet: Mapped["Outlet"] = relationship("Outlet")
    guest: Mapped["Guest"] = relationship("Guest")
    cashier: Mapped[Optional["User"]] = relationship("User")
    room: Mapped[Optional["Room"]] = relationship("Room")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    delivery: Mapped[Optional["DeliveryTracking"]] = relationship("DeliveryTracking", back_populates="order", uselist=False)

    @property
    def branch_id(self) -> uuid.UUID:
        return self.outlet_id

    @branch_id.setter
    def branch_id(self, value: uuid.UUID) -> None:
        self.outlet_id = value

    @property
    def customer_id(self) -> uuid.UUID:
        return self.guest_id

    @customer_id.setter
    def customer_id(self, value: uuid.UUID) -> None:
        self.guest_id = value

    @property
    def total_amount(self) -> float:
        return self.total_usd_cents / 100

    @total_amount.setter
    def total_amount(self, value: float) -> None:
        self.total_usd_cents = int(round(float(value) * 100))
