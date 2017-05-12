"""Create comic entry for mel

Revision ID: 03bbe0bc1832
Revises: c182f32a7c45
Create Date: 2017-05-12 15:20:22.722262

"""

# revision identifiers, used by Alembic.
revision = '03bbe0bc1832'
down_revision = 'c182f32a7c45'
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
            {'name': 'mel', 'type': 'rss', 'channelgid': '-1001105187138',
             'lastchecked': '1981/01/24', 'url': 'http://elchistedemel.blogspot.com/feeds/posts/default'}
        ]
    )


def downgrade():
    pass
