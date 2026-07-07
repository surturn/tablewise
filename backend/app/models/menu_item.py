import uuid
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import BaseModelMixin


class MenuItem(Base, BaseModelMixin):
    __tablename__ = "menu_items"

    outlet_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("menu_categories.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price_kes_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    category: Mapped["MenuCategory"] = relationship("MenuCategory", back_populates="items")
    outlet: Mapped["Outlet"] = relationship("Outlet")

    @property
    def price(self) -> float:
        return self.price_kes_cents / 100

    @price.setter
    def price(self, value: float) -> None:
        self.price_kes_cents = int(round(float(value) * 100))

    @property
    def is_active(self) -> bool:
        return self.is_available

    @is_active.setter
    def is_active(self, value: bool) -> None:
        self.is_available = value
