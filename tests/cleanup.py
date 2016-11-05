#!/usr/bin/env python
# encoding: utf-8

from stampy.stampy import setconfig, createdb, dbsql


def clean():
    # Precreate DB for other operations to work
    try:
        createdb()
    except:
        pass

    # Define configuration for tests
    setconfig('token', '279488169:AAFqGVesZ-83n9sFxfLQxUUCVO8_8L3JNEU')
    setconfig('owner', 'iranzo')
    setconfig('url', 'https://api.telegram.org/bot')
    setconfig('verbosity', 'DEBUG')

    # Empty karma database in case it contained some leftover
    dbsql('DELETE from karma')
    dbsql('DELETE from alias')
    dbsql('DELETE from quote')
    dbsql('UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME="quote"')
