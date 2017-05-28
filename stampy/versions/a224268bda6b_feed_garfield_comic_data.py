# coding=utf-8
"""Feed Garfield comic data

Revision ID: a224268bda6b
Revises: 214568dbb0b7
Create Date: 2017-05-14 00:46:42.975679

"""

# revision identifiers, used by Alembic.
revision = 'a224268bda6b'
down_revision = '214568dbb0b7'
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
                  sa.Column('url', sa.Text),
                  sa.Column('imgxpath', sa.Text),
                  sa.Column('txtxpath', sa.Text)
                  )
    op.bulk_insert(
        comic,
        [
            {'name': 'garfield', 'type': 'url', 'channelgid': '-1001105187138',
             'lastchecked': '1981/01/24',
             'url': 'https://s3.amazonaws.com/static.garfield.com/comics/garfield/#year#/#year#-#month#-#day#.gif',
             'imgxpath': 'False',
             'txtxpath': 'False'}
        ]
    )


def downgrade():
    """
    Performs database downgrade
    """

    pass
