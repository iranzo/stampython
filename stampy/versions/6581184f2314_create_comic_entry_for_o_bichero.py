# coding=utf-8
"""Create comic entry for O bichero

Revision ID: 6581184f2314
Revises: afe311f9077d
Create Date: 2017-05-12 15:20:48.313564

"""

# revision identifiers, used by Alembic.
revision = '6581184f2314'
down_revision = 'afe311f9077d'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import table


def upgrade():
    """
    Performs upgrade of database
    """
    
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
            {'name': 'obichero', 'type': 'rss', 'channelgid': '-1001069507044',
             'lastchecked': '1981/01/24',
             'url': 'http://obichero.blogspot.com/feeds/posts/default'}
        ]
    )


def downgrade():
    """
    Performs database downgrade
    """
    pass
