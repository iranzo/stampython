"""Add interval to feed table

Revision ID: b44c7b6baa0f
Revises: bc2446053c0a
Create Date: 2017-07-01 07:57:34.802996

"""

# revision identifiers, used by Alembic.
revision = 'b44c7b6baa0f'
down_revision = 'bc2446053c0a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    """
        Performs upgrade of database
        """

    op.add_column(u'feeds', sa.Column('interval', sa.Text(), nullable=True))
    op.execute("""
                    UPDATE
                       "feeds"
                    SET
                        interval = 30
                """)


def downgrade():
    """
    Performs database downgrade
    """

    op.drop_column(u'feeds', 'interval')
