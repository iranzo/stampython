# coding=utf-8
"""Create comic entry for xkcd

Revision ID: 43da6a6a45ea
Revises: 03bbe0bc1832
Create Date: 2017-05-12 15:20:26.506414

"""

# revision identifiers, used by Alembic.
revision = '43da6a6a45ea'
down_revision = '03bbe0bc1832'
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
            {'name': 'xkcd', 'type': 'rss', 'channelgid': '-1001105187138',
             'lastchecked': '1981/01/24', 'url': 'https://xkcd.com/atom.xml'}
        ]
    )


def downgrade():
    """
    Performs database downgrade
    """

    pass
