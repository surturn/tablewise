"""Replace Stripe with M-Pesa as the payment provider

Revision ID: 7f2a1c9e4b3d
Revises: 4365cb273f86
Create Date: 2026-07-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f2a1c9e4b3d'
down_revision: Union[str, None] = '4365cb273f86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE paymentmethod RENAME VALUE 'stripe' TO 'mpesa'")

    op.alter_column('payments', 'stripe_payment_intent_id', new_column_name='mpesa_checkout_request_id')
    op.alter_column('payments', 'stripe_charge_id', new_column_name='mpesa_receipt_number')
    op.add_column('payments', sa.Column('mpesa_merchant_request_id', sa.String(length=255), nullable=True))
    op.add_column('payments', sa.Column('phone_number', sa.String(length=20), nullable=True))
    op.execute("ALTER INDEX ix_payments_stripe_payment_intent_id RENAME TO ix_payments_mpesa_checkout_request_id")

    op.alter_column('bookings', 'stripe_payment_intent_id', new_column_name='mpesa_checkout_request_id')
    op.execute("ALTER INDEX ix_bookings_stripe_payment_intent_id RENAME TO ix_bookings_mpesa_checkout_request_id")


def downgrade() -> None:
    op.execute("ALTER INDEX ix_bookings_mpesa_checkout_request_id RENAME TO ix_bookings_stripe_payment_intent_id")
    op.alter_column('bookings', 'mpesa_checkout_request_id', new_column_name='stripe_payment_intent_id')

    op.execute("ALTER INDEX ix_payments_mpesa_checkout_request_id RENAME TO ix_payments_stripe_payment_intent_id")
    op.drop_column('payments', 'phone_number')
    op.drop_column('payments', 'mpesa_merchant_request_id')
    op.alter_column('payments', 'mpesa_receipt_number', new_column_name='stripe_charge_id')
    op.alter_column('payments', 'mpesa_checkout_request_id', new_column_name='stripe_payment_intent_id')

    op.execute("ALTER TYPE paymentmethod RENAME VALUE 'mpesa' TO 'stripe'")
