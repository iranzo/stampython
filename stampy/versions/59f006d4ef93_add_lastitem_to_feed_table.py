"""Add lastitem to feed table

Revision ID: 59f006d4ef93
Revises: b44c7b6baa0f
Create Date: 2017-07-11 16:25:03.213846

"""

# revision identifiers, used by Alembic.
revision = '59f006d4ef93'
down_revision = 'b44c7b6baa0f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    """
    Performs upgrade of database
    """

    op.add_column(u'feeds', sa.Column('lastitem', sa.Text(), nullable=True))


def downgrade():
    """
    Performs database downgrade
    """

    op.drop_column(u'feeds', 'lastitem')
