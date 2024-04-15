"""Добавил автары к пользователям gjg

Revision ID: 260d74c3ade0
Revises: 
Create Date: 2024-04-16 00:31:48.027817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '260d74c3ade0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
