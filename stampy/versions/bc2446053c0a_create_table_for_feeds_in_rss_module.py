"""Create table for feeds in rss module

Revision ID: bc2446053c0a
Revises: b73beec49812
Create Date: 2017-06-19 22:35:02.011042

"""

# revision identifiers, used by Alembic.
revision = 'bc2446053c0a'
down_revision = 'b73beec49812'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    """
    Performs upgrade of database
    """

    op.create_table(
        'feeds',
        sa.Column('name', sa.Text),
        sa.Column('url', sa.Text),
        sa.Column('gid', sa.Text),
        sa.Column('lastchecked', sa.Text),
    )


def downgrade():
    """
    Performs database downgrade
    """

    op.drop_table('feeds')
