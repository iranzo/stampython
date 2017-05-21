"""Create comic entry for Bernardo Vergara

Revision ID: 495fea37afc5
Revises: a224268bda6b
Create Date: 2017-05-22 14:30:28.130081

"""

# revision identifiers, used by Alembic.
revision = '495fea37afc5'
down_revision = 'a224268bda6b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table


def upgrade():
    comic = table('comic',
                  sa.Column('name', sa.Text),
                  sa.Column('type', sa.Text),
                  sa.Column('channelgid', sa.Text),
                  sa.Column('lastchecked', sa.Text),
                  sa.Column('url', sa.Text)
                  )
    op.bulk_insert(
        comic,
        [
            {'name': 'vergara', 'type': 'rss', 'channelgid': '-1001105187138',
             'lastchecked': '1981/01/24', 'url': 'http://www.eldiario.es/rss/section/20038/'}
        ]
    )


def downgrade():
    pass
