"""Create cron table

Revision ID: 4ce73d5a92f4
Revises: 59f006d4ef93
Create Date: 2017-08-05 16:04:39.277508

"""

# revision identifiers, used by Alembic.
revision = '4ce73d5a92f4'
down_revision = '59f006d4ef93'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'cron',
        sa.Column('name', sa.Text),
        sa.Column('interval', sa.Text),
        sa.Column('lastchecked', sa.Text(), nullable=True)
    )


def downgrade():
    """
    Performs database downgrade
    """

    op.drop_table('cron')
