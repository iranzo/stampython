# coding=utf-8
"""Modify config table so it is chan_id specific

Revision ID: d87d296fb8a9
Revises: 31779fbd5770
Create Date: 2017-03-23 08:06:02.044034

"""

# revision identifiers, used by Alembic.
revision = 'd87d296fb8a9'
down_revision = '31779fbd5770'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(u'config', sa.Column('id', sa.Text(), nullable=True))
    op.execute("""
        UPDATE
           "config"
        SET
            id = 0
    """)


def downgrade():
    op.drop_column(u'config', 'id')
