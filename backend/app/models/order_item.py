import uuid
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import BaseModelMixin


class OrderItem(Base, BaseModelMixin):
    __tablename__ = "order_items"

    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    menu_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("menu_items.id", ondelete="RESTRICT"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price_usd_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal_usd_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    special_instructions: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship("MenuItem")

    @property
    def unit_price(self) -> float:
        return self.unit_price_usd_cents / 100

    @unit_price.setter
    def unit_price(self, value: float) -> None:
        self.unit_price_usd_cents = int(round(float(value) * 100))

    @property
    def subtotal(self) -> float:
        return self.subtotal_usd_cents / 100

    @subtotal.setter
    def subtotal(self, value: float) -> None:
        self.subtotal_usd_cents = int(round(float(value) * 100))
