"""Добавил автары к пользователям

Revision ID: c4c86652176c
Revises: 260d74c3ade0
Create Date: 2024-04-16 00:36:06.258557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4c86652176c'
down_revision: Union[str, None] = '260d74c3ade0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
