"""Merge multiple heads

Revision ID: 814b61673a32
Revises: 709176dd395b, baabf6dd8324
Create Date: 2024-11-12 18:59:59.142351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '814b61673a32'
down_revision: Union[str, None] = ('709176dd395b', 'baabf6dd8324')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass