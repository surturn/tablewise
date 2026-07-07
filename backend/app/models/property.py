from typing import Any, Dict, List
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import BaseModelMixin


class Property(Base, BaseModelMixin):
    __tablename__ = "properties"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False, default="Juba, South Sudan")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Africa/Juba")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="KES")
    settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    outlets: Mapped[List["Outlet"]] = relationship("Outlet", back_populates="property")
    room_types: Mapped[List["RoomType"]] = relationship("RoomType", back_populates="property")
