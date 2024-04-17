"""Жанры

Revision ID: 7e22b001360b
Revises: 44499147eb2c
Create Date: 2024-04-17 00:40:45.666186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e22b001360b'
down_revision: Union[str, None] = '44499147eb2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
