"""Forward table setup

Revision ID: 31779fbd5770
Revises: 920edc7ead15
Create Date: 2017-03-21 15:24:16.694202

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '31779fbd5770'
down_revision = '920edc7ead15'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'forward',
        sa.Column('source', sa.Text),
        sa.Column('target', sa.Text),
    )


def downgrade():
    op.drop_table('forward')
