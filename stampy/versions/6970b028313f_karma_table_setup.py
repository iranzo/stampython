# coding=utf-8
"""Karma table setup

Revision ID: 6970b028313f
Revises: d750f83c294a
Create Date: 2017-03-21 15:24:14.914225

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6970b028313f'
down_revision = 'd750f83c294a'
branch_labels = None
depends_on = None


def upgrade():
    """
    Performs upgrade of database
    """
    
    op.create_table(
        'karma',
        sa.Column('word', sa.Text),
        sa.Column('value', sa.Integer),
        sa.Column('date', sa.Text),
    )


def downgrade():
    """
    Performs database downgrade
    """
    op.drop_table('karma')
