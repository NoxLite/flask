"""Добавил таблицу комментариев к песни

Revision ID: b4e335599645
Revises: f21ca30bd090
Create Date: 2024-04-19 15:54:53.479510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4e335599645'
down_revision: Union[str, None] = 'f21ca30bd090'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
