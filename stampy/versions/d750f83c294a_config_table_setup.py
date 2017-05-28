# coding=utf-8
"""Config table setup

Revision ID: d750f83c294a
Revises:
Create Date: 2017-03-21 15:23:18.769280

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'd750f83c294a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    Performs upgrade of database
    """
    
    op.create_table(
        'config',
        sa.Column('key', sa.Text),
        sa.Column('value', sa.Text),
    )


def downgrade():
    """
    Performs database downgrade
    """
    op.drop_table('config')
