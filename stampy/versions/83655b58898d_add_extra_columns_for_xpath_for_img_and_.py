# coding=utf-8
"""Add extra columns for xpath for img and txt

Revision ID: 83655b58898d
Revises: 6581184f2314
Create Date: 2017-05-13 22:08:36.289277

"""

# revision identifiers, used by Alembic.
revision = '83655b58898d'
down_revision = '6581184f2314'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(u'comic', sa.Column('imgxpath', sa.Text(), nullable=True))
    op.add_column(u'comic', sa.Column('txtxpath', sa.Text(), nullable=True))


def downgrade():
    pass
