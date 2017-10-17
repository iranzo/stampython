"""Add CommitStrip support

Revision ID: 342210a18b82
Revises: 4ce73d5a92f4
Create Date: 2017-10-17 11:52:57.063879

"""

# revision identifiers, used by Alembic.
revision = '342210a18b82'
down_revision = '4ce73d5a92f4'
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
            {'name': 'CommitStrip', 'type': 'rssurl',
             'channelgid': '-1001105187138',
             'lastchecked': '1981/01/24',
             'url': 'http://www.commitstrip.com/en/feed/',
             'imgxpath': '//div/p/img/@src',
             'txtxpath': '//h1[@class="entry-title"]/text()'
             }
        ]
    )


def downgrade():
    pass
