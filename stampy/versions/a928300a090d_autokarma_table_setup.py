# coding=utf-8
"""Autokarma table setup

Revision ID: a928300a090d
Revises: 414cb0d3a23e
Create Date: 2017-03-21 15:24:15.621920

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a928300a090d'
down_revision = '414cb0d3a23e'
branch_labels = None
depends_on = None


def upgrade():
    """
    Performs upgrade of database
    """

    op.create_table(
        'autokarma',
        sa.Column('key', sa.Text),
        sa.Column('value', sa.Text),
    )


def downgrade():
    """
    Performs database downgrade
    """

    op.drop_table('autokarma')
