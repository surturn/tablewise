"""add resilient payment fields

Revision ID: 5f8c1a9d2b77
Revises: 20cbbf30cc37
Create Date: 2026-05-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5f8c1a9d2b77"
down_revision: Union[str, None] = "20cbbf30cc37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE paymentmethod ADD VALUE IF NOT EXISTS 'MOBILE_MONEY'")
    op.execute("ALTER TYPE paymentmethod ADD VALUE IF NOT EXISTS 'STRIPE'")
    op.add_column("payments", sa.Column("stripe_checkout_session_id", sa.String(length=255), nullable=True))
    op.add_column("payments", sa.Column("stripe_payment_intent_id", sa.String(length=255), nullable=True))
    op.add_column("payments", sa.Column("mobile_money_provider", sa.String(length=50), nullable=True))
    op.add_column("payments", sa.Column("external_reference", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_payments_stripe_checkout_session_id"), "payments", ["stripe_checkout_session_id"], unique=True)
    op.create_index(op.f("ix_payments_stripe_payment_intent_id"), "payments", ["stripe_payment_intent_id"], unique=True)
    op.create_index(op.f("ix_payments_external_reference"), "payments", ["external_reference"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_payments_external_reference"), table_name="payments")
    op.drop_index(op.f("ix_payments_stripe_payment_intent_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_stripe_checkout_session_id"), table_name="payments")
    op.drop_column("payments", "external_reference")
    op.drop_column("payments", "mobile_money_provider")
    op.drop_column("payments", "stripe_payment_intent_id")
    op.drop_column("payments", "stripe_checkout_session_id")
