"""Create comic entry for El Jueves

Revision ID: afe311f9077d
Revises: 43da6a6a45ea
Create Date: 2017-05-12 15:20:31.047066

"""

# revision identifiers, used by Alembic.
revision = 'afe311f9077d'
down_revision = '43da6a6a45ea'
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
            {'name': 'jueves', 'type': 'rss', 'channelgid': '-1001105187138',
             'lastchecked': '1981/01/24',
             'url': 'http://www.eljueves.es/feeds/vineta-del-dia.html'}
        ]
    )


def downgrade():
    pass
