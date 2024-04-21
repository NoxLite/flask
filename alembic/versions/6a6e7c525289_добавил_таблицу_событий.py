"""Добавил таблицу событий

Revision ID: 6a6e7c525289
Revises: 99ff62436319
Create Date: 2024-04-21 01:24:16.899817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a6e7c525289'
down_revision: Union[str, None] = '99ff62436319'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
