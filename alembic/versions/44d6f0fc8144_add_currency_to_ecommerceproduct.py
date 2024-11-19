"""Add currency to EcommerceProduct

Revision ID: 44d6f0fc8144
Revises: 926ad1b04c58
Create Date: 2024-11-16 22:39:40.936777

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44d6f0fc8144'
down_revision: Union[str, None] = '926ad1b04c58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ecommerce_products', sa.Column('currency', sa.String(length=10), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ecommerce_products', 'currency')
    # ### end Alembic commands ###