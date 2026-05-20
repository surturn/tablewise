"""merge_heads

Revision ID: e4a0040a5477
Revises: 5f8c1a9d2b77, 9f1f2a3b4c5d
Create Date: 2026-05-19 13:21:12.791866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4a0040a5477'
down_revision: Union[str, None] = ('5f8c1a9d2b77', '9f1f2a3b4c5d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass