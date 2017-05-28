# coding=utf-8
"""Use gid in autok

Revision ID: 81a858b4f7f4
Revises: 7f6c3fd04ee8
Create Date: 2017-04-24 23:36:47.162442

"""

# revision identifiers, used by Alembic.
revision = '81a858b4f7f4'
down_revision = '7f6c3fd04ee8'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    """
    Performs upgrade of database
    """

    op.add_column(u'autokarma', sa.Column('gid', sa.Text(), nullable=True))
    op.execute("""
                UPDATE
                   "autokarma"
                SET
                    gid = 0
            """)


def downgrade():
    """
    Performs database downgrade
    """

    op.drop_column(u'autokarma', 'gid')
