import uuid
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import BaseModelMixin
from app.models.enums import UserRole


class User(Base, BaseModelMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    outlet_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("outlets.id", ondelete="SET NULL"), nullable=True, index=True
    )

    outlet: Mapped[Optional["Outlet"]] = relationship("Outlet", back_populates="users")

    @property
    def branch_id(self) -> Optional[uuid.UUID]:
        return self.outlet_id

    @branch_id.setter
    def branch_id(self, value: Optional[uuid.UUID]) -> None:
        self.outlet_id = value

    @property
    def branch(self):
        return self.outlet
