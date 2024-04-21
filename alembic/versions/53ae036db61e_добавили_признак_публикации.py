"""добавили признак публикации

Revision ID: 53ae036db61e
Revises: 7e22b001360b
Create Date: 2024-04-19 15:52:19.381631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53ae036db61e'
down_revision: Union[str, None] = '7e22b001360b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
