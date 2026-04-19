import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import BaseModelMixin


class InventoryItem(Base, BaseModelMixin):
    __tablename__ = "inventory_items"

    # Inventory is strictly scoped per branch
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("branches.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sku: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    
    # Current physical stock
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    
    # E.g., 'kg', 'liters', 'pieces'
    unit: Mapped[str] = mapped_column(String(20), nullable=False) 
    
    # Threshold to trigger Celery low-stock alerts
    low_stock_threshold: Mapped[float] = mapped_column(Numeric(10, 2), default=10.0)

    # Relationships
    branch: Mapped["Branch"] = relationship("Branch")