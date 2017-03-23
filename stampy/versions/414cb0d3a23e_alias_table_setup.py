"""Alias table setup

Revision ID: 414cb0d3a23e
Revises: 6970b028313f
Create Date: 2017-03-21 15:24:15.265400

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '414cb0d3a23e'
down_revision = '6970b028313f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'alias',
        sa.Column('key', sa.Text),
        sa.Column('value', sa.Text),
    )


def downgrade():
    op.drop_table('alias')
