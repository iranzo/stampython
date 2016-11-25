#!/usr/bin/env python
# encoding: utf-8

import stampy.stampy
import stampy.plugin.config


def clean():
    """
    Cleans the most common databases to allow a start fresh scenario
    :return:
    """
    # Precreate DB for other operations to work
    try:
        stampy.stampy.createdb()
    except:
        pass

    # Define configuration for tests
    stampy.plugin.config.setconfig('token', '279488169:AAFqGVesZ-83n9sFxfLQxUUCVO8_8L3JNEU')
    stampy.plugin.config.setconfig('owner', 'iranzo')
    stampy.plugin.config.setconfig('url', 'https://api.telegram.org/bot')
    stampy.plugin.config.setconfig('verbosity', 'DEBUG')

    # Empty karma database in case it contained some leftover
    stampy.stampy.dbsql('DELETE from karma')
    stampy.stampy.dbsql('DELETE from alias')
    stampy.stampy.dbsql('DELETE from autokarma')
    stampy.stampy.dbsql('DELETE from stats')
    stampy.stampy.dbsql('DELETE from quote')
    stampy.stampy.dbsql('UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME="quote"')
