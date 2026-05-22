"""add customer auth fields

Revision ID: 6a3b2b4d1c9f
Revises: 94471fb24b14
Create Date: 2026-05-21 10:40:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6a3b2b4d1c9f'
down_revision = '94471fb24b14'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('guests', sa.Column('hashed_password', sa.String(length=255), nullable=True))
    op.add_column('guests', sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False))

def downgrade() -> None:
    op.drop_column('guests', 'is_active')
    op.drop_column('guests', 'hashed_password')
