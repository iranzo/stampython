# coding=utf-8
"""Create comic table

Revision ID: c182f32a7c45
Revises: 7b1ba3bab31e
Create Date: 2017-05-11 15:54:09.001256

"""

# revision identifiers, used by Alembic.
revision = 'c182f32a7c45'
down_revision = '7b1ba3bab31e'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    """
    Performs upgrade of database
    """

    op.create_table(
        'comic',
        sa.Column('name', sa.Text),
        sa.Column('type', sa.Text),
        sa.Column('channelgid', sa.Text),
        sa.Column('lastchecked', sa.Text),
        sa.Column('url', sa.Text)
    )


def downgrade():
    """
    Performs database downgrade
    """

    op.drop_table('comic')
