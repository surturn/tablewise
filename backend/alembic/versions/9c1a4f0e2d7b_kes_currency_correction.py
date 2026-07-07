"""Correct currency fields: rename usd_cents columns to kes_cents and fix magnitude

KES is the platform's authoritative currency (see docs/payment-currency-and-booking-prd.md).
The `*_usd_cents` columns were named and populated as if the stored integer were USD cents, but
mpesa_service has always sent that same integer to Safaricom's Daraja API as whole KES with no
FX conversion. Renaming the columns alone would not fix this: the *values* also need to be
multiplied by 100 so a room that reads as "8500" (intended to be KES 8,500.00) is actually stored
as 850000 KES-cents rather than KES 85.00. See docs/payment-currency-and-booking-prd.md FR-1/FR-2.

Revision ID: 9c1a4f0e2d7b
Revises: 7f2a1c9e4b3d
Create Date: 2026-07-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '9c1a4f0e2d7b'
down_revision: Union[str, None] = '7f2a1c9e4b3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (table, old_column, new_column)
_RENAMES = [
    ("menu_items", "price_usd_cents", "price_kes_cents"),
    ("orders", "total_usd_cents", "total_kes_cents"),
    ("order_items", "unit_price_usd_cents", "unit_price_kes_cents"),
    ("order_items", "subtotal_usd_cents", "subtotal_kes_cents"),
    ("room_types", "base_price_usd_cents", "base_price_kes_cents"),
    ("bookings", "total_usd_cents", "total_kes_cents"),
    ("booking_extras", "price_usd_cents", "price_kes_cents"),
    ("payments", "amount_usd_cents", "amount_kes_cents"),
    ("guests", "total_spend_usd_cents", "total_spend_kes_cents"),
]


def upgrade() -> None:
    for table, old_column, new_column in _RENAMES:
        op.alter_column(table, old_column, new_column_name=new_column)
    for table, _old_column, new_column in _RENAMES:
        op.execute(f'UPDATE "{table}" SET {new_column} = {new_column} * 100')
    op.execute("UPDATE properties SET currency = 'KES' WHERE currency = 'USD'")


def downgrade() -> None:
    op.execute("UPDATE properties SET currency = 'USD' WHERE currency = 'KES'")
    for table, _old_column, new_column in _RENAMES:
        op.execute(f'UPDATE "{table}" SET {new_column} = {new_column} / 100')
    for table, old_column, new_column in _RENAMES:
        op.alter_column(table, new_column, new_column_name=old_column)
