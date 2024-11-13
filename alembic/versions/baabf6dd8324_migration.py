"""migration

Revision ID: baabf6dd8324
<<<<<<< HEAD
Revises: cd87d11e3c6b
=======
Revises: 4f3cd5570838
>>>>>>> 683a7c8462bc2b233b657969544153859d880718
Create Date: 2024-11-10 12:25:01.919524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'baabf6dd8324'
<<<<<<< HEAD
down_revision: Union[str, None] = 'cd87d11e3c6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
=======
down_revision: Union[str, None] = '4f3cd5570838'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ecommerce_products', sa.Column('ebay_item_id', sa.String(length=50), nullable=False))
    op.create_unique_constraint(None, 'ecommerce_products', ['ebay_item_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ecommerce_products', type_='unique')
    op.drop_column('ecommerce_products', 'ebay_item_id')
>>>>>>> 683a7c8462bc2b233b657969544153859d880718
    # ### end Alembic commands ###