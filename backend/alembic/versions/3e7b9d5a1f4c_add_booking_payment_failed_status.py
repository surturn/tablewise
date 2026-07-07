"""Add 'failed' to bookingpaymentstatus enum

handle_payment_failure previously only updated Order on a failed M-Pesa payment, never Booking
(see docs/payment-currency-and-booking-prd.md FR-6/FR-7). Fixing that requires a payment_status
value distinct from 'unpaid' so reception staff can tell "payment attempted and failed" apart
from "never attempted."

Revision ID: 3e7b9d5a1f4c
Revises: 9c1a4f0e2d7b
Create Date: 2026-07-04 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '3e7b9d5a1f4c'
down_revision: Union[str, None] = '9c1a4f0e2d7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE bookingpaymentstatus ADD VALUE IF NOT EXISTS 'failed'")


def downgrade() -> None:
    # Postgres cannot drop a single enum value in place. Any bookings left in the
    # 'failed' state must be reconciled to 'unpaid' before downgrading, or this will fail.
    op.execute("UPDATE bookings SET payment_status = 'unpaid' WHERE payment_status = 'failed'")
    op.execute("ALTER TYPE bookingpaymentstatus RENAME TO bookingpaymentstatus_old")
    op.execute("CREATE TYPE bookingpaymentstatus AS ENUM ('unpaid', 'partial', 'paid', 'refunded')")
    op.execute(
        "ALTER TABLE bookings ALTER COLUMN payment_status "
        "TYPE bookingpaymentstatus USING payment_status::text::bookingpaymentstatus"
    )
    op.execute("DROP TYPE bookingpaymentstatus_old")
