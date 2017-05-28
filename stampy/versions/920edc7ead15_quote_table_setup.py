# coding=utf-8
"""quote table setup

Revision ID: 920edc7ead15
Revises: 31a14014c9ce
Create Date: 2017-03-21 15:24:16.341183

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '920edc7ead15'
down_revision = '31a14014c9ce'
branch_labels = None
depends_on = None


def upgrade():
    """
    Performs upgrade of database
    """

    op.create_table(
        'quote',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('username', sa.Text),
        sa.Column('date', sa.Text),
        sa.Column('text', sa.Text),
    )


def downgrade():
    """
    Performs database downgrade
    """

    op.drop_table('quote')
