#!/usr/bin/env python
# encoding: utf-8

import stampy.stampy
import stampy.plugin.config
import stampy.plugins

# As we're not executing stampy.main, initialize the plugins available to
# process karma
stampy.stampy.plugs, stampy.stampy.plugtriggers = stampy.plugins.initplugins()


def clean():
    """
    Cleans the most common databases to allow a start fresh scenario
    :return:
    """
    # Precreate DB for other operations to work
    try:
        stampy.stampy.createorupdatedb()
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
