#!/usr/bin/env python
#
# Description: Bot for controlling karma on Telegram
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

# TODO
# Mostly everything :), initial steps are there for accessing URL
# - Database integration and updating with new values
# - Confirm last processed message and save it in database as well as sending request to telegram api to mark as read
# - Create functions for the calls to increase/decrease karma
# - Create functions for sending back karma count to originating channel
# - Run loop to get new messages and post updates
# - Consider moving to webhook for async operation

import optparse
import json
import urllib
import sqlite3 as lite
import sys
from time import sleep

description = """
Stampy is a script for controlling Karma via Telegram.org bot api

"""

# Option parsing
p = optparse.OptionParser("stampy.py [arguments]", description=description)
p.add_option("-t", "--token", dest="token", help="API token for bot access to messages", default=None)
p.add_option("-b", "--database", dest="database", help="database file for storing karma and last processed message",
             default="stampy.db")
p.add_option('-v', "--verbosity", dest="verbosity", help="Show messages while running", metavar='[0-n]', default=0,
             type='int')
p.add_option('-u', "--url", dest="url", help="Define URL for accessing bot API", default="https://api.telegram.org/bot")
p.add_option('-c', '--control', dest='control', help="Define chat_id for monitoring service", default=None)
p.add_option('-d', '--daemon', dest='daemon', help="Run as daemon", default=False, action="store_true")

(options, args) = p.parse_args()


if options.token:
    token = options.token
else:
    print "Token required for operation, please check https://core.telegram.org/bots"
    sys.exit(1)


def sendmessage(options, chat_id=0, text="", reply_to_message_id=None):
    url = "%s%s/sendMessage" % (options.url, options.token)
    message = "%s?chat_id=%s&text=%s" % (url, chat_id, urllib.quote_plus(text))
    if reply_to_message_id:
            message = message + "&reply_to_message_id=%s" % reply_to_message_id
    return json.load(urllib.urlopen(message))


def getupdates(options, offset=0, limit=100):
    url = "%s%s/getUpdates" % (options.url, options.token)
    message = "%s?" % url
    if offset != 0:
        message = message + "offset=%s&" % offset
    message = message + "limit=%s" % limit
    result = None
    try:
        result = json.load(urllib.urlopen(message))
    except:
        result = None
    for item in result['result']:
        yield item


def clearupdates(options, offset):
    url = "%s%s/getUpdates" % (options.url, options.token)
    message = "%s?" % url
    message = message + "offset=%s&" % offset
    try:
        result = json.load(urllib.urlopen(message))
    except:
        result = None
    return result


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
    date = 0
    lastupdateid = 0
    print "Initial message at %s" % date
    texto = ""
    error = 0
    for message in getupdates(options):
        update_id = message['update_id']
        try:
            texto = message['message']['text'].lower()
            chat_id = message['message']['chat']['id']
            message_id = int(message['message']['message_id'])
        except:
            error = 1

        if update_id > lastupdateid:
            lastupdateid = update_id
        newdate = int(float(message['message']['date']))
        if newdate > date:
            date = newdate
            for word in texto.split():
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
                        sendmessage(options, chat_id=chat_id, text=text, reply_to_message_id=message_id)
        clearupdates(options, offset=update_id)

    print "Last processed message at %s" % date
    print "Last processed update id %s" % lastupdateid
    print "Last processed text %s" % texto

    clearupdates(options, offset=lastupdateid + 1)

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

if options.daemon:
    print "Running in daemon mode"
    while 1 > 0:
        process()
        sleep(10)
else:
    print "Running in one-shoot mode"
    process()

# Close database
if con:
    con.close()
