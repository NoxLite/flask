"""добавил новую таблицу Song

Revision ID: 5fd5c846c57c
Revises: f8e4a2e600fe
Create Date: 2024-04-10 23:06:23.832212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5fd5c846c57c'
down_revision: Union[str, None] = 'f8e4a2e600fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
