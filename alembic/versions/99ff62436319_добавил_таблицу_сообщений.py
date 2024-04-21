"""Добавил таблицу сообщений

Revision ID: 99ff62436319
Revises: b4e335599645
Create Date: 2024-04-21 00:47:56.711846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99ff62436319'
down_revision: Union[str, None] = 'b4e335599645'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
