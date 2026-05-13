"""refactor_tablewise_to_grandplatform

Revision ID: 9f1f2a3b4c5d
Revises: 20cbbf30cc37
Create Date: 2026-05-11 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "9f1f2a3b4c5d"
down_revision: Union[str, None] = "20cbbf30cc37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "properties",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.rename_table("branches", "outlets")
    op.rename_table("customers", "guests")
    outlet_type = postgresql.ENUM("restaurant", "bar", name="outlettype", create_type=False)
    outlet_type.create(op.get_bind(), checkfirst=True)
    op.add_column("outlets", sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("outlets", sa.Column("type", outlet_type, nullable=False, server_default="restaurant"))
    op.create_foreign_key("fk_outlets_property_id", "outlets", "properties", ["property_id"], ["id"], ondelete="CASCADE")
    op.add_column("guests", sa.Column("nationality", sa.String(length=80), nullable=True))
    op.add_column("guests", sa.Column("id_document_type", sa.String(length=50), nullable=True))
    op.add_column("guests", sa.Column("total_spend_usd_cents", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("outlet_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_users_outlet_id", "users", "outlets", ["outlet_id"], ["id"], ondelete="SET NULL")
    op.create_table(
        "room_types",
        sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("base_price_usd_cents", sa.Integer(), nullable=False),
        sa.Column("amenities", sa.JSON(), nullable=True),
        sa.Column("photos", sa.JSON(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    room_status = postgresql.ENUM("available", "occupied", "cleaning", "maintenance", name="roomstatus", create_type=False)
    room_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "rooms",
        sa.Column("room_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("room_number", sa.String(length=20), nullable=False),
        sa.Column("floor", sa.Integer(), nullable=False),
        sa.Column("status", room_status, nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["room_type_id"], ["room_types.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("room_number"),
    )
    booking_status = postgresql.ENUM("pending", "confirmed", "checked_in", "checked_out", "cancelled", name="bookingstatus", create_type=False)
    booking_payment_status = postgresql.ENUM("unpaid", "partial", "paid", "refunded", name="bookingpaymentstatus", create_type=False)
    booking_status.create(op.get_bind(), checkfirst=True)
    booking_payment_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "bookings",
        sa.Column("room_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("guest_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("check_in", sa.Date(), nullable=False),
        sa.Column("check_out", sa.Date(), nullable=False),
        sa.Column("status", booking_status, nullable=True),
        sa.Column("total_usd_cents", sa.Integer(), nullable=False),
        sa.Column("payment_status", booking_payment_status, nullable=True),
        sa.Column("stripe_payment_intent_id", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["guest_id"], ["guests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("booking_extras", sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("name", sa.String(length=100), nullable=False), sa.Column("price_usd_cents", sa.Integer(), nullable=False), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_table("stock_movements", sa.Column("inventory_item_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("change_quantity", sa.Integer(), nullable=False), sa.Column("reason", sa.String(length=80), nullable=False), sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["inventory_item_id"], ["inventory_items.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"), sa.PrimaryKeyConstraint("id"))
    op.create_table("audit_logs", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True), sa.Column("action", sa.String(length=100), nullable=False), sa.Column("entity_type", sa.String(length=80), nullable=False), sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True), sa.Column("old_value", sa.JSON(), nullable=True), sa.Column("new_value", sa.JSON(), nullable=True), sa.Column("ip_address", sa.String(length=64), nullable=True), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"), sa.PrimaryKeyConstraint("id"))


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("stock_movements")
    op.drop_table("booking_extras")
    op.drop_table("bookings")
    op.drop_table("rooms")
    op.drop_table("room_types")
    op.drop_constraint("fk_users_outlet_id", "users", type_="foreignkey")
    op.drop_column("users", "outlet_id")
    op.drop_constraint("fk_outlets_property_id", "outlets", type_="foreignkey")
    op.drop_column("outlets", "type")
    op.drop_column("outlets", "property_id")
    op.drop_column("guests", "total_spend_usd_cents")
    op.drop_column("guests", "id_document_type")
    op.drop_column("guests", "nationality")
    op.rename_table("guests", "customers")
    op.rename_table("outlets", "branches")
    op.drop_table("properties")
