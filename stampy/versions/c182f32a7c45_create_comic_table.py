"""Create comic table

Revision ID: c182f32a7c45
Revises: 7b1ba3bab31e
Create Date: 2017-05-11 15:54:09.001256

"""

# revision identifiers, used by Alembic.
revision = 'c182f32a7c45'
down_revision = '7b1ba3bab31e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
        op.create_table(
            'comic',
            sa.Column('name', sa.Text),
            sa.Column('type', sa.Text),
            sa.Column('channelgid', sa.Text),
            sa.Column('lastchecked', sa.Text),
            sa.Column('url', sa.Text)
        )

"""
INSERT INTO table VALUES('jueves','rss','-1001105187138','','http://www.eljueves.es/feeds/vineta-del-dia.html');
INSERT INTO table VALUES('mel','rss','-1001105187138','','http://elchistedemel.blogspot.com/feeds/posts/default');
INSERT INTO table VALUES('obichero','rss','-1001069507044','','http://obichero.blogspot.com/feeds/posts/default');
INSERT INTO table VALUES('xkcd','rss','-1001105187138','','https://xkcd.com/atom.xml');
"""


def downgrade():
    op.drop_table('comic')
