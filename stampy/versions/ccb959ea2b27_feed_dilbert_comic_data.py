"""Feed Dilbert comic data

Revision ID: ccb959ea2b27
Revises: 83655b58898d
Create Date: 2017-05-13 22:23:05.983065

"""

# revision identifiers, used by Alembic.
revision = 'ccb959ea2b27'
down_revision = '83655b58898d'
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
                  sa.Column('url', sa.Text),
                  sa.Column('imgxpath', sa.Text),
                  sa.Column('txtxpath', sa.Text)
                  )
    op.bulk_insert(
        comic,
        [
            {'name': 'dilbert', 'type': 'url', 'channelgid': '-1001066352913',
             'lastchecked': '1981/01/24',
             'url': 'http://dilbert.com/strip/#year#-#month#-#day#',
             'imgxpath': '//img[@class="img-responsive img-comic"]/@src',
             'txtxpath': '//img[@class="img-responsive img-comic"]/@alt'}
        ]
    )


def downgrade():
    pass
