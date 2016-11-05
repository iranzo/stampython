#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from stampy.stampy import config, setconfig, createdb, dbsql

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
dbsql('DELETE from quote')
dbsql('UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME="quote"')


class TestStampy(TestCase):
    def test_owner(self):
        self.assertEqual(config('owner'), 'iranzo')
