import uuid
from typing import List, Optional
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import BaseModelMixin
from app.models.enums import OutletType


class Outlet(Base, BaseModelMixin):
    __tablename__ = "outlets"

    property_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=True, index=True
    )
    type: Mapped[OutletType] = mapped_column(SQLEnum(OutletType), nullable=False, default=OutletType.restaurant)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_number: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    opening_time: Mapped[str] = mapped_column(String(10), default="08:00")
    closing_time: Mapped[str] = mapped_column(String(10), default="22:00")

    property: Mapped[Optional["Property"]] = relationship("Property", back_populates="outlets")
    users: Mapped[List["User"]] = relationship("User", back_populates="outlet")


# Transitional alias for legacy imports while the API moves to /outlets.
Branch = Outlet
