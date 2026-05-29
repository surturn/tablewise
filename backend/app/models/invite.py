from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import BaseModelMixin
from app.models.enums import UserRole

class InviteToken(Base, BaseModelMixin):
    __tablename__ = "invite_tokens"

    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    outlet_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("outlets.id", ondelete="CASCADE"), nullable=True, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    outlet: Mapped[Optional["Outlet"]] = relationship("Outlet")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by_id])
