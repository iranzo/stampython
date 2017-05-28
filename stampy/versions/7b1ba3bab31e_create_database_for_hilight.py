# coding=utf-8
"""Create database for hilight

Revision ID: 7b1ba3bab31e
Revises: 355236948ec7
Create Date: 2017-04-27 16:46:41.341143

"""

# revision identifiers, used by Alembic.
revision = '7b1ba3bab31e'
down_revision = '355236948ec7'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    """
    Performs upgrade of database
    """
    
    op.create_table(
        'hilight',
        sa.Column('word', sa.Text),
        sa.Column('gid', sa.Text(), nullable=True)
    )


def downgrade():
    """
    Performs database downgrade
    """
    op.drop_table('hilight')
