"""Feed Quico Jubilata comic data

Revision ID: 214568dbb0b7
Revises: ccb959ea2b27
Create Date: 2017-05-13 22:29:10.135860

"""

# revision identifiers, used by Alembic.
revision = '214568dbb0b7'
down_revision = 'ccb959ea2b27'
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
            {'name': 'quico', 'type': 'url', 'channelgid': '-1001105187138',
             'lastchecked': '1981/01/24',
             'url': 'http://www.quicojubilata.com/quico-jubilata/#year#-#month#-#day#',
             'imgxpath': '//img[@class="img-responsive"]/@src',
             'txtxpath': '//h1[@class="js-quickedit-page-title page-header"]/span'}
        ]
    )


def downgrade():
    pass
