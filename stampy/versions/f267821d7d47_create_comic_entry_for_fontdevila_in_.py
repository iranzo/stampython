# coding=utf-8
"""Create comic entry for Fontdevila in eldiario.es

Revision ID: f267821d7d47
Revises: a5ed252d562f
Create Date: 2017-05-25 10:21:36.886564

"""

# revision identifiers, used by Alembic.
revision = 'f267821d7d47'
down_revision = 'a5ed252d562f'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op
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
            {'name': 'fontdevila', 'type': 'rss', 'channelgid': '-1001105187138',
             'lastchecked': '1981/01/24', 'url': 'http://www.eldiario.es/rss/section/20039/'}
        ]
    )


def downgrade():
    pass
