# coding: utf-8
from sqlalchemy import Column, Integer, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import NullType

Base = declarative_base()
metadata = Base.metadata

t_alias = Table(
    'alias', metadata,
    Column('key', Text),
    Column('value', Text)
)

t_autokarma = Table(
    'autokarma', metadata,
    Column('key', Text),
    Column('value', Text)
)

t_config = Table(
    'config', metadata,
    Column('key', Text),
    Column('value', Text)
)

t_forward = Table(
    'forward', metadata,
    Column('source', Text),
    Column('target', Text)
)

t_karma = Table(
    'karma', metadata,
    Column('word', Text),
    Column('value', Integer),
    Column('date', Text)
)


class Quote(Base):
    __tablename__ = 'quote'

    id = Column(Integer, primary_key=True)
    username = Column(Text)
    date = Column(Text)
    text = Column(Text)


t_sqlite_sequence = Table(
    'sqlite_sequence', metadata,
    Column('name', NullType),
    Column('seq', NullType)
)

t_stats = Table(
    'stats', metadata,
    Column('type', Text),
    Column('id', Integer),
    Column('name', Text),
    Column('date', Text),
    Column('count', Integer),
    Column('memberid', Text)
)
