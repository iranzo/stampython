#!/usr/bin/env python
#
# Description: Script for pre-loading karma in database
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.

import optparse
import json
import urllib
import sqlite3 as lite
import sys
from time import sleep

description = """
This script pre-loads database with karma from files

"""

# Option parsing
p = optparse.OptionParser("stampy.py [arguments]", description=description)
p.add_option("-b", "--database", dest="database", help="database file for storing karma and last processed message",
             default="stampy.db")
p.add_option('-v', "--verbosity", dest="verbosity", help="Show messages while running", metavar='[0-n]', default=0,
             type='int')
p.add_option('-f', "--file", dest="file", help="Define file to load karma from", default=None)

(options, args) = p.parse_args()


if options.token:
    token = options.token
else:
    print "Token required for operation, please check https://core.telegram.org/bots"
    sys.exit(1)


def updatekarma(options, word=None, change=0):
    value = getkarma(options, word=word)
    return putkarma(options, word, value + change)


def getkarma(options, word):
    sql = "SELECT * FROM karma WHERE word='%s'" % word
    cur.execute(sql)
    value = cur.fetchone()
    try:
        # Get value from SQL query
        value = value[1]
    except:
        createkarma(options, word)
        value = 0
    return value


def createkarma(options, word):
    sql = "INSERT INTO karma VALUES('%s',0)" % word
    cur.execute(sql)
    return con.commit()


def createdb(options):
    return cur.execute('CREATE TABLE karma(word TEXT, value INT)')


def putkarma(options, word, value):
    sql = "UPDATE karma SET value = '%s' WHERE word = '%s'" % (value, word)
    cur.execute(sql)
    con.commit()
    return value


def process():
    # TODO
    # read from file and process loop
    with open(options.file) as f:
        for line in f:
            for word in line.split():
                if len(word) >= 4:
                    change = 0
                    if "++" == word[-2:]:
                        print "++ Found in %s at %s with id %s" % (word, chat_id, message_id)
                        change = 1
                    if "--" == word[-2:]:
                        print "-- Found in %s at %s with id %s" % (word, chat_id, message_id)
                        change = -1
                    if change != 0:
                        # Remove last two characters from word (++ or --)
                        word = word[0:-2]
                        karma = updatekarma(options, word=word, change=change)
                        if karma != 0:
                            text = "%s now has %s karma points." % (word, karma)
                        else:
                            text = "%s now has no Karma and has been garbage collected." % word

    print "Last processed message at %s" % date
    print "Last processed update id %s" % lastupdateid
    print "Last processed text %s" % texto


# Main code

# Initialize database access
con = None
try:
    con = lite.connect(options.database)
    cur = con.cursor()
    cur.execute("SELECT * FROM karma WHERE word='stampy'")
    data = cur.fetchone()

except lite.Error, e:
    createdb(options)
    print "Error %s:" % e.args[0]
    sys.exit(1)

# Database initialized

# Main program
process()

# Close database
if con:
    con.close()
