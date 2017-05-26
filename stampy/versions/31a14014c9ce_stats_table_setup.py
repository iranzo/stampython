# coding=utf-8
"""Stats table setup

Revision ID: 31a14014c9ce
Revises: a928300a090d
Create Date: 2017-03-21 15:24:16.000283

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '31a14014c9ce'
down_revision = 'a928300a090d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'stats',
        sa.Column('type', sa.Text),
        sa.Column('id', sa.Integer),
        sa.Column('name', sa.Text),
        sa.Column('date', sa.Text),
        sa.Column('count', sa.Integer),
        sa.Column('memberid', sa.Text),
    )


def downgrade():
    op.drop_table('stats')
