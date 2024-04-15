"""Добавил аватар

Revision ID: 44499147eb2c
Revises: c4c86652176c
Create Date: 2024-04-16 00:51:55.188699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44499147eb2c'
down_revision: Union[str, None] = 'c4c86652176c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
