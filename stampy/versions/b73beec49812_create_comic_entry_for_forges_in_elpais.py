"""Create comic entry for Forges in ElPais

Revision ID: b73beec49812
Revises: f267821d7d47
Create Date: 2017-05-27 17:07:34.895426

"""

# revision identifiers, used by Alembic.
revision = 'b73beec49812'
down_revision = 'f267821d7d47'
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
            {'name': 'forges', 'type': 'rssurl', 'channelgid': '-1001105187138',
             'lastchecked': '1981/01/24',
             'url': 'http://ep00.epimg.net/rss/tags/a_antonio_fraguas_forges_a.xml',
             'imgxpath': '//div[@id="articulo_contenedor"]//img/@src',
             'txtxpath': '//div[@id="articulo_contenedor"]//img/@alt'}
        ]
    )


def downgrade():
    """
    Performs database downgrade
    """
    pass
