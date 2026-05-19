import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import BaseModelMixin


class InventoryItem(Base, BaseModelMixin):
    __tablename__ = "inventory_items"

    outlet_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sku: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    low_stock_threshold: Mapped[float] = mapped_column(Numeric(10, 2), default=10.0)

    outlet: Mapped["Outlet"] = relationship("Outlet")

    @property
    def branch_id(self) -> uuid.UUID:
        return self.outlet_id

    @branch_id.setter
    def branch_id(self, value: uuid.UUID) -> None:
        self.outlet_id = value

    @property
    def branch(self):
        return self.outlet
