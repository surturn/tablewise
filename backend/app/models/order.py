import uuid
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import BaseModelMixin
from app.models.enums import OrderStatus

class Order(Base, BaseModelMixin):
    __tablename__ = "orders"

    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("branches.id", ondelete="RESTRICT"), index=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), index=True
    )
    # Cashier who processed it (if done in-store), null if online
    cashier_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.CREATED)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Delivery info
    is_delivery: Mapped[bool] = mapped_column(default=False)
    delivery_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    branch: Mapped["Branch"] = relationship("Branch")
    customer: Mapped["Customer"] = relationship("Customer")
    cashier: Mapped[Optional["User"]] = relationship("User")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment: Mapped[Optional["Payment"]] = relationship("Payment", back_populates="order", uselist=False)
    delivery: Mapped[Optional["DeliveryTracking"]] = relationship("DeliveryTracking", back_populates="order", uselist=False)