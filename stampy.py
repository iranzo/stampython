#!/usr/bin/env python
# encoding: utf-8
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

import optparse
import json
import urllib
import sqlite3 as lite
import sys
import time
import datetime
from time import sleep

description = """
Stampy is a script for controlling Karma via Telegram.org bot api

"""

# Option parsing
p = optparse.OptionParser("stampy.py [arguments]", description=description)
p.add_option("-t", "--token", dest="token",
             help="API token for bot access to messages", default=None)
p.add_option("-b", "--database", dest="database",
             help="database file for storing karma and last processed message",
             default="stampy.db")
p.add_option('-v', "--verbosity", dest="verbosity",
             help="Show messages while running", metavar='[0-n]', default=0,
             type='int')
p.add_option('-u', "--url", dest="url",
             help="Define URL for accessing bot API",
             default="https://api.telegram.org/bot")
p.add_option('-c', '--control', dest='control',
             help="Define chat_id for monitoring service", default=None)
p.add_option('-d', '--daemon', dest='daemon', help="Run as daemon",
             default=False, action="store_true")

(options, args) = p.parse_args()

# Implement switch from http://code.activestate.com/recipes/410692/


class Switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


# Function definition
def sendmessage(options, chat_id=0, text="", reply_to_message_id=None,
                disable_web_page_preview=True):
    url = "%s%s/sendMessage" % (options.url, options.token)
    message = "%s?chat_id=%s&text=%s" % (url, chat_id,
                                         urllib.quote_plus(text.encode('utf8'))
                                         )
    if reply_to_message_id:
            message = message + "&reply_to_message_id=%s" % reply_to_message_id
    if disable_web_page_preview:
            message = message + "&disable_web_page_preview=1"
    log(options, facility="sendmessage", verbosity=3,
        text="Sending message: %s" % text)
    return json.load(urllib.urlopen(message))


def getupdates(options, offset=0, limit=100):
    url = "%s%s/getUpdates" % (options.url, options.token)
    message = "%s?" % url
    if offset != 0:
        message = message + "offset=%s&" % offset
    message = message + "limit=%s" % limit
    try:
        result = json.load(urllib.urlopen(message))['result']
    except:
        result = []
    for item in result:
        log(options, facility="getupdates", verbosity=9,
            text="Getting updates and returning: %s" % item)
        yield item


def clearupdates(options, offset):
    url = "%s%s/getUpdates" % (options.url, options.token)
    message = "%s?" % url
    message = message + "offset=%s&" % offset
    try:
        result = json.load(urllib.urlopen(message))
    except:
        result = None
    log(options, facility="clearupdates", verbosity=9, text="Clearing messages")
    return result


def updatekarma(options, word=None, change=0):
    value = getkarma(options, word=word)
    return putkarma(options, word, value + change)


def getkarma(options, word):
    string = (word, )
    sql = "SELECT * FROM karma WHERE word='%s'" % string
    cur.execute(sql)
    value = cur.fetchone()

    try:
        # Get value from SQL query
        value = value[1]

    except:
        # Value didn't exist before, return 0
        value = 0

    return value


def createdb(options):
    # Create database if it doesn't exist
    return cur.execute('CREATE TABLE karma(word TEXT, value INT)')


def createkarma(options, word):
    sql = "INSERT INTO karma VALUES('%s',0)" % word
    cur.execute(sql)
    return con.commit()


def putkarma(options, word, value):
    if getkarma(options, word) == 0:
        createkarma(options, word)
    if value != 0:
        sql = "UPDATE karma SET value = '%s' WHERE word = '%s'" % (value, word)
    else:
        sql = "DELETE FROM karma WHERE  word = '%s'" % word
    cur.execute(sql)
    con.commit()
    return value


def telegramcommands(options, texto, chat_id, message_id):
    # Process lines for commands in the first word of the line (Telegram)
    word = texto.split()[0]
    commandtext = None
    for case in Switch(word):
        if case('/help'):
            commandtext = "To use this bot use word++ or word-- to increment or decrement karma, a new message will be sent providing the new total\n\n"
            commandtext = commandtext + "Use rank word or rank to get value for actual word or top 10 rankings\n\n"
            commandtext = commandtext + "Use srank word to search for similar words already ranked\n\n"
            commandtext = commandtext + "Learn more about this bot in https://github.com/iranzo/stampython"
            break
        if case('/start'):
            commandtext = "This bot does not use start or stop commands, it automatically checks for karma operands"
            break
        if case('/stop'):
            commandtext = "This bot does not use start or stop commands, it automatically checks for karma operands"
            break
        if case():
            commandtext = None

    # If any of above commands did match, send command
    if commandtext:
        sendmessage(options, chat_id=chat_id, text=commandtext,
                    reply_to_message_id=message_id)
        log(options, facility="telegramcommands", verbosity=9,
            text="Command: %s" % word)
    return


def karmacommands(options, texto, chat_id, message_id):
    # Process lines for commands in the first word of the line (Telegram commands)
    word = texto.split()[0]
    commandtext = None

    # Check first word for commands
    for case in Switch(word):
        if case('rank'):
            try:
                word = texto.split()[1]
            except:
                word = None
            commandtext = rank(options, word)
            break
        if case('srank'):
            try:
                word = texto.split()[1]
            except:
                word = None
            commandtext = srank(options, word)
            break
        if case():
            commandtext = None

    # If any of above cases did a match, send command
    if commandtext:
        sendmessage(options, chat_id=chat_id, text=commandtext,
                    reply_to_message_id=message_id)
        log(options, facility="karmacommands", verbosity=9,
                              text="karmacommand:  %s" % word)
    return


def rank(options, word=None):

    if word:
        # if word is provided, return the rank value for that word
        string = (word,)
        sql = "SELECT * FROM karma WHERE word='%s'" % string
        cur.execute(sql)
        value = cur.fetchone()

        try:
            # Get value from SQL query
            value = value[1]

        except:
            # Value didn't exist before, return 0 value
            value = 0
        text = "%s has %s karma points." % (word, value)

    else:
        # if word is not provided, return top 10 words with top karma
        sql = "select * from karma ORDER BY value DESC LIMIT 10;"

        text = "Global rankings:\n"
        line = 0
        for item in cur.execute(sql):
            try:
                value = item[1]
                word = item[0]
                line = line + 1
                text = text + "%s. %s (%s)\n" % (line, word, value)
            except:
                continue
    log(options, facility="rank", verbosity=9,
        text="Returning karma %s for word %s" % (text, word))
    return text


def srank(options, word=None):
    text = ""
    if word is None:
        # If no word is provided to srank, call rank instead
        text = rank(options, word)
    else:
        string = "%" + word + "%"
        sql = "SELECT * FROM karma WHERE word LIKE '%s' LIMIT 10" % string

        for item in cur.execute(sql):
            try:
                value = item[1]
                word = item[0]
                text = text + "%s: (%s)\n" % (word, value)
            except:
                continue
    log(options, facility="srank", verbosity=9,
        text="Returning srank for word: %s" % word)
    return text


def log(options, facility=options.database, severity="INFO", verbosity=0, text=""):
    when = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    if options.verbosity >= verbosity:
        print "%s %s : %s : %s : %s" % (when, options.database, facility, severity, text)
    return


def sendsticker(options, chat_id=0, sticker="", text="", reply_to_message_id="", reply_markup=""):
    url = "%s%s/sendSticker" % (options.url, options.token)
    message = "%s?chat_id=%s" % (url, chat_id)
    message = "%s&sticker=%s" % (message, sticker)
    if reply_to_message_id:
        message = message + "&reply_to_message_id=%s" % reply_to_message_id
    log(options, facility="sendsticker", verbosity=3, text="Sending sticker: %s" % text)
    return json.load(urllib.urlopen(message))


def stampy(options, chat_id="", karma=0, reply_to_message_id=False):

    karma = "%s" % karma
    # Sticker definitions for each rank
    X00 = "BQADBAADYwAD17FYAAEidrCCUFH7AgI"
    X000 = "BQADBAADZQAD17FYAAEeeRNtkOWfBAI"
    X0000 = "BQADBAADZwAD17FYAAHHuNL2oLuShwI"
    X00000 = "BQADBAADaQAD17FYAAHzIBRZeY4uNAI"

    sticker = ""
    if karma[-5:] == "00000":
        sticker = X00000
    elif karma[-4:] == "0000":
        sticker = X0000
    elif karma[-3:] == "000":
        sticker = X000
    elif karma[-2:] == "00":
        sticker = X00

    text = "Sticker for %s karma points" % karma

    if sticker != "":
        sendsticker(options, chat_id=chat_id, sticker=sticker, text="%s" % text)
    return


def process():
    # Main code for processing the karma updates
    date = 0
    lastupdateid = 0
    log(options, facility="main", verbosity=0,
        text="Initial message at %s" % date)
    texto = ""
    error = False
    count = 0

    # Process each message available in URL and search for karma operators
    for message in getupdates(options):
        # Count messages in each batch
        count = count + 1
        update_id = message['update_id']
        try:
            texto = message['message']['text'].lower()
            chat_id = message['message']['chat']['id']
            message_id = int(message['message']['message_id'])
            date = int(float(message['message']['date']))
            chat_name = message['message']['chat']['title']
            who_gn = message['message']['from']['first_name']
            who_id = message['message']['from']['id']

        except:
            error = True

        try:
            who_ln = message['message']['from']['last_name']
        except:
            who_ln = None

        # Some user might not have username defined so this
        # was failing and message was ignored
        try:
            who_un = message['message']['from']['username']

        except:
            who_un = None

        # Update last message id to later clear it from the server
        if update_id > lastupdateid:
            lastupdateid = update_id

        if not error:
            # Search for telegram commands
            telegramcommands(options, texto, chat_id, message_id)

            # Search for karma commands
            karmacommands(options, texto, chat_id, message_id)

            # Process each word in the line received to search for karma operators
            for word in texto.split():
                if word[0] == "@":
                    # Remove @ from mentions for karma
                    word = word[1:]
                word = word.replace("'", '')
                # Unicode — is sometimes provided by telegram cli, using that also as comparision
                unidecrease = u"—"
                if word[-1:] == unidecrease:
                    word = word.replace(unidecrease, '--')

                log(options, facility="main", verbosity=9,
                    text="Processing word %s sent by id %s with username %s (%s %s)" % (word, who_id, who_un, who_gn, who_ln))
                if len(word) >= 4:
                    # Determine karma change and apply it
                    change = 0
                    if "++" == word[-2:]:
                        log(options, facility="main", verbosity=1,
                            text="++ Found in %s at %s with id %s (%s), sent by id %s named %s (%s %s)" % (word, chat_id, message_id, chat_name, who_id, who_un, who_gn, who_ln))
                        change = 1
                    if "--" == word[-2:]:
                        log(options, facility="main", verbosity=1,
                            text="-- Found in %s at %s with id %s (%s), sent by id %s named %s (%s %s)" % (word, chat_id, message_id, chat_name, who_id, who_un, who_gn, who_ln))
                        change = -1
                    if change != 0:
                        # Remove last two characters from word (++ or --)
                        word = word[0:-2]
                        karma = updatekarma(options, word=word, change=change)
                        if karma != 0:
                            # Karma has changed, report back
                            text = "%s now has %s karma points." % (word, karma)
                        else:
                            # New karma is 0
                            text = "%s now has no Karma and has been garbage collected." % word
                        # Send originating user for karma change a reply with
                        # the new value
                        sendmessage(options, chat_id=chat_id, text=text,
                                    reply_to_message_id=message_id)
                        stampy(options, chat_id=chat_id, karma=karma, reply_to_message_id=message_id)

    log(options, facility="main", verbosity=0,
        text="Last processed message at: %s" % date)
    log(options, facility="main", verbosity=0,
        text="Last processed update_id : %s" % lastupdateid)
    log(options, facility="main", verbosity=0,
        text="Last processed text: %s" % texto)
    log(options, facility="main", verbosity=0,
        text="Number of messages in this batch: %s" % count)

    # clear updates (marking messages as read)
    clearupdates(options, offset=lastupdateid + 1)

# Main code

# Check if we've the token required to access or exit
if options.token:
    token = options.token
else:
    log(options, facility="main", severity="ERROR", verbosity=0,
        text="Token required for operation, please check https://core.telegram.org/bots")
    sys.exit(1)


# Initialize database access
con = None
try:
    con = lite.connect(options.database)
    cur = con.cursor()
    cur.execute("SELECT * FROM karma WHERE word='stampy'")
    data = cur.fetchone()

except lite.Error, e:
    createdb(options)
    log(options, facility="main", verbosity=0, text="Error %s:" % e.args[0])
    sys.exit(1)

# Database initialized

# Check operation mode and call process as required
if options.daemon:
    log(options, facility="main", verbosity=0, text="Running in daemon mode")
    while 1 > 0:
        process()
        sleep(10)
else:
    log(options, facility="main", verbosity=0,
        text="Running in one-shoot mode")
    process()

# Close database
if con:
    con.close()
