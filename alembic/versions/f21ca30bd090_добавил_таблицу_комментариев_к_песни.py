"""Добавил таблицу комментариев к песни

Revision ID: f21ca30bd090
Revises: 53ae036db61e
Create Date: 2024-04-19 15:52:47.966269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f21ca30bd090'
down_revision: Union[str, None] = '53ae036db61e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
