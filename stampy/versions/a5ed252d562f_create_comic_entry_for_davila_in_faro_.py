"""Create comic entry for Davila in Faro de Vigo

Revision ID: a5ed252d562f
Revises: 495fea37afc5
Create Date: 2017-05-24 16:53:14.633489

"""

# revision identifiers, used by Alembic.
revision = 'a5ed252d562f'
down_revision = '495fea37afc5'
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
            {'name': 'davila', 'type': 'url', 'channelgid': '-1001069507044',
             'lastchecked': '1981/01/24',
             'url': 'http://fotos.farodevigo.es/vinyetas/#year#/#month#/#day#/davila.jpg',
             'imgxpath': 'False',
             'txtxpath': 'False'}
        ]
    )



def downgrade():
    pass
