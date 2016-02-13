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
p.add_option('-o', '--owner', dest='owner',
             help="Define owner username for monitoring service", default="iranzo")
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


# Initialize database access
con = None
try:
    con = lite.connect(options.database)
    cur = con.cursor()
    cur.execute("SELECT * FROM karma WHERE word='stampy'")
    data = cur.fetchone()

except lite.Error, e:
    createdb()
    log(facility="main", verbosity=0, text="Error %s:" % e.args[0])
    sys.exit(1)


# Database initialized


# Function definition
def sendmessage(chat_id=0, text="", reply_to_message_id=None,
                disable_web_page_preview=True):
    url = "%s%s/sendMessage" % (config(key='url'), config(key='token'))
    message = "%s?chat_id=%s&text=%s" % (url, chat_id,
                                         urllib.quote_plus(text.encode('utf8'))
                                         )
    if reply_to_message_id:
        message += "&reply_to_message_id=%s" % reply_to_message_id
    if disable_web_page_preview:
        message += "&disable_web_page_preview=1"
    log(facility="sendmessage", verbosity=3,
        text="Sending message: %s" % text)
    return json.load(urllib.urlopen(message))


def getupdates(offset=0, limit=100):
    url = "%s%s/getUpdates" % (config(key='url'), config(key='token'))
    message = "%s?" % url
    if offset != 0:
        message += "offset=%s&" % offset
    message += "limit=%s" % limit
    try:
        result = json.load(urllib.urlopen(message))['result']
    except:
        result = []
    for item in result:
        log(facility="getupdates", verbosity=9,
            text="Getting updates and returning: %s" % item)
        yield item


def clearupdates(offset):
    url = "%s%s/getUpdates" % (config(key='url'), config(key='token'))
    message = "%s?" % url
    message += "offset=%s&" % offset
    try:
        result = json.load(urllib.urlopen(message))
    except:
        result = None
    log(facility="clearupdates", verbosity=9, text="Clearing messages")
    return result


def updatekarma(word=None, change=0):
    value = getkarma(word=word)
    return putkarma(word, value + change)


def getkarma(word):
    string = (word,)
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


def createdb():
    # Create database if it doesn't exist
    cur.execute('CREATE TABLE karma(word TEXT, value INT)')
    cur.execute('CREATE TABLE alias(key TEXT, value TEXT)')
    cur.execute('CREATE TABLE config(key TEXT, value TEXT)')
    cur.execute('CREATE TABLE stats(type TEXT, id INT, name TEXT, date TEXT, count INT)')
    return


def config(key):
    string = (key,)
    sql = "SELECT * FROM config WHERE key='%s'" % string
    cur.execute(sql)
    value = cur.fetchone()

    try:
        # Get value from SQL query
        value = value[1]

    except:
        # Value didn't exist before, return 0
        value = False

    return value


def saveconfig(key, value):
    if value:
        sql = "UPDATE config SET value = '%s' WHERE key = '%s'" % (value, key)
        cur.execute(sql)
        con.commit()
    return value


def createkarma(word):
    sql = "INSERT INTO karma VALUES('%s',0)" % word
    cur.execute(sql)
    return con.commit()


def putkarma(word, value):
    if getkarma(word) == 0:
        createkarma(word)
    if value != 0:
        sql = "UPDATE karma SET value = '%s' WHERE word = '%s'" % (value, word)
    else:
        sql = "DELETE FROM karma WHERE  word = '%s'" % word
    cur.execute(sql)
    con.commit()
    return value


def getstats(type=None, id=0, name=None, date=None, count=0):
    sql = "SELECT * FROM stats WHERE id='%s' AND type='%s';" % (id, type)
    cur.execute(sql)

    try:
        value = cur.fetchone()
    except:
        value = False

    if value:
        (type, id, name, date, count) = value
    log(facility="getstats", verbosity=9, text="value")
    return value


def updatestats(type=None, id=0, name=None, date=None, count=0):
    try:
        value = getstats(type=type, id=id)
        count = value[4] + 1
        old_id = value[1]
    except:
        value = False
        old_id = False

    if not value:
        sql = "INSERT INTO stats VALUES ('%s', '%s', '%s', '%s', '%s');" % (type, id, name, date, count)
    if old_id != 0 and type:
        sql = "UPDATE stats SET type='%s', name='%s', date='%s', count='%s'  WHERE id = '%s';" % (
        type, name, date, count, id)
    log(facility="updatestats", verbosity=9, text="value")
    cur.execute(sql)
    return con.commit()


def telegramcommands(texto, chat_id, message_id, who_un):
    # Process lines for commands in the first word of the line (Telegram)
    word = texto.split()[0]
    commandtext = None
    for case in Switch(word):
        if case('/help'):
            commandtext = "To use this bot use word++ or word-- to increment or decrement karma, a new message will be sent providing the new total\n\n"
            commandtext += "Use rank word or rank to get value for actual word or top 10 rankings\n\n"
            commandtext += "Use srank word to search for similar words already ranked\n\n"
            commandtext += "Learn more about this bot in https://github.com/iranzo/stampython"
            break
        if case('/start'):
            commandtext = "This bot does not use start or stop commands, it automatically checks for karma operands"
            break
        if case('/stop'):
            commandtext = "This bot does not use start or stop commands, it automatically checks for karma operands"
            break
        if case('/alias'):
            aliascommands(texto, chat_id, message_id, who_un)
            break
        if case('/config'):
            configcommands(texto, chat_id, message_id, who_un)
            break
        if case('/stats'):
            statscommands(texto, chat_id, message_id, who_un)
            break
        if case():
            commandtext = None

    # If any of above commands did match, send command
    if commandtext:
        sendmessage(chat_id=chat_id, text=commandtext,
                    reply_to_message_id=message_id)
        log(facility="commands", verbosity=9,
            text="Command: %s" % word)
    return


def getalias(word):
    string = (word,)
    sql = "SELECT * FROM alias WHERE key='%s'" % string
    cur.execute(sql)
    value = cur.fetchone()
    log(facility="alias", verbosity=9, text="getalias: %s" % word)

    try:
        # Get value from SQL query
        value = value[1]

    except:
        # Value didn't exist before, return 0
        value = False

    # We can define recursive aliases, so this will return the ultimate one
    if value:
        return getalias(word=value)
    return word


def createalias(word, value):
    if getalias(value) == word:
        log(facility="alias", verbosity=9, text="createalias: circular reference %s=%s" % (word, value))
    else:
        if not getalias(word):
            sql = "INSERT INTO alias VALUES('%s','%s')" % (word, value)
            cur.execute(sql)
            log(facility="alias", verbosity=9, text="createalias: %s=%s" % (word, value))
            return con.commit()
    return False


def deletealias(word):
    sql = "DELETE FROM alias WHERE key='%s'" % word
    cur.execute(sql)
    log(facility="alias", verbosity=9, text="rmalias: %s" % word)
    return con.commit()


def listalias(word=False):
    if word:
        # if word is provided, return the alias for that word
        string = (word,)
        sql = "SELECT * FROM alias WHERE key='%s'" % string
        cur.execute(sql)
        value = cur.fetchone()

        try:
            # Get value from SQL query
            value = value[1]

        except:
            # Value didn't exist before, return 0 value
            value = 0
        text = "%s has an alias %s" % (word, value)

    else:
        sql = "select * from alias ORDER BY key DESC"

        text = "Defined aliases:\n"
        line = 0
        for item in cur.execute(sql):
            try:
                value = item[1]
                word = item[0]
                line += 1
                text += "%s. %s (%s)\n" % (line, word, value)
            except:
                continue
    log(facility="alias", verbosity=9,
        text="Returning aliases %s for word %s" % (text, word))
    return text


def setconfig(key, value):
    if config(key=key):
        deleteconfig(key)
    sql = "INSERT INTO config VALUES('%s','%s')" % (key, value)
    cur.execute(sql)
    log(facility="config", verbosity=9, text="setconfig: %s=%s" % (key, value))
    return con.commit()


def deleteconfig(word):
    sql = "DELETE FROM config WHERE key='%s'" % word
    cur.execute(sql)
    log(facility="config", verbosity=9, text="rmconfig: %s" % word)
    return con.commit()


def showconfig(key=False):
    if key:
        # if word is provided, return the config for that key
        string = (key,)
        sql = "SELECT * FROM config WHERE key='%s'" % string
        cur.execute(sql)
        value = cur.fetchone()

        try:
            # Get value from SQL query
            value = value[1]

        except:
            # Value didn't exist before, return 0 value
            value = 0
        text = "%s has a value of %s" % (key, value)

    else:
        sql = "select * from config ORDER BY key DESC"

        text = "Defined configurations:\n"
        line = 0
        for item in cur.execute(sql):
            try:
                value = item[1]
                key = item[0]
                line += 1
                text += "%s. %s (%s)\n" % (line, key, value)
            except:
                continue
    log(facility="config", verbosity=9,
        text="Returning config %s for key %s" % (text, key))
    return text


def aliascommands(texto, chat_id, message_id, who_un):
    log(facility="alias", verbosity=9,
        text="Command: %s by %s" % (texto, who_un))
    if who_un == config('owner'):
        log(facility="alias", verbosity=9,
            text="Command: %s by %s" % (texto, who_un))
        command = texto.split(' ')[1]
        try:
            word = texto.split(' ')[2]
        except:
            word = ""

        for case in Switch(command):
            if case('list'):
                text = listalias(word)
                sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True)
                break
            if case('delete'):
                key = word
                text = "Deleting alias for %s" % key
                sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True)
                deletealias(word=key)
                break
            if case():
                word = texto.split(' ')[1]
                if "=" in word:
                    key = word.split('=')[0]
                    value = word.split('=')[1]
                    text = "Setting alias for %s to %s" % (key, value)
                    sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id,
                                disable_web_page_preview=True)
                    # Removing duplicates on karma DB and add the previous values
                    old = getkarma(key)
                    updatekarma(word=key, change=-old)
                    updatekarma(word=value, change=old)
                    createalias(word=key, value=value)

    return


def configcommands(texto, chat_id, message_id, who_un):
    log(facility="config", verbosity=9,
        text="Command: %s by %s" % (texto, who_un))
    if who_un == config('owner'):
        log(facility="config", verbosity=9,
            text="Command: %s by %s" % (texto, who_un))
        command = texto.split(' ')[1]
        try:
            word = texto.split(' ')[2]
        except:
            word = ""

        for case in Switch(command):
            if case('show'):
                text = showconfig(word)
                sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True)
                break
            if case('delete'):
                key = word
                text = "Deleting config for %s" % key
                sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True)
                deleteconfig(word=key)
                break
            if case('set'):
                word = texto.split(' ')[2]
                if "=" in word:
                    key = word.split('=')[0]
                    value = word.split('=')[1]
                    setconfig(key=key, value=value)
                    text = "Setting config for %s to %s" % (key, value)
                    sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id,
                                disable_web_page_preview=True)
                break
            if case():
                break

    return


def showstats(type=False):
    if type:
        sql = "select * from stats WHERE type='%s' ORDER BY type DESC" % type
    else:
        sql = "select * from stats ORDER BY type DESC"

    text = "Defined stats:\n"
    line = 0
    for item in cur.execute(sql):
        try:
            (type, id, name, date, count) = item
            line += 1
            text += "%s. Type: %s ID: %s(%s) Date: %s Count: %s\n" % (line, type, id, name, date, count)
        except:
            continue
    log(facility="stats", verbosity=9,
        text="Returning stats %s for type %s" % (text, type))
    return text


def statscommands(texto, chat_id, message_id, who_un):
    log(facility="stats", verbosity=9,
        text="Command: %s by %s" % (texto, who_un))
    if who_un == config('owner'):
        log(facility="stats", verbosity=9,
            text="Command: %s by %s" % (texto, who_un))
        command = texto.split(' ')[1]
        try:
            key = texto.split(' ')[2]
        except:
            key = ""

        for case in Switch(command):
            if case('show'):
                text = showstats(key)
                sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True)
                break
            if case():
                break

    return


def karmacommands(texto, chat_id, message_id):
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
            commandtext = rank(word)
            break
        if case('srank'):
            try:
                word = texto.split()[1]
            except:
                word = None
            commandtext = srank(word)
            break
        if case():
            commandtext = None

    # If any of above cases did a match, send command
    if commandtext:
        sendmessage(chat_id=chat_id, text=commandtext,
                    reply_to_message_id=message_id)
        log(facility="karmacommands", verbosity=9,
            text="karmacommand:  %s" % word)
    return


def rank(word=None):
    if getalias(word):
        word = getalias(word)
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
                line += 1
                text += "%s. %s (%s)\n" % (line, word, value)
            except:
                continue
    log(facility="rank", verbosity=9,
        text="Returning karma %s for word %s" % (text, word))
    return text


def srank(word=None):
    if getalias(word):
        word = getalias(word)
    text = ""
    if word is None:
        # If no word is provided to srank, call rank instead
        text = rank(word)
    else:
        string = "%" + word + "%"
        sql = "SELECT * FROM karma WHERE word LIKE '%s' LIMIT 10" % string

        for item in cur.execute(sql):
            try:
                value = item[1]
                word = item[0]
                text += "%s: (%s)\n" % (word, value)
            except:
                continue
    log(facility="srank", verbosity=9,
        text="Returning srank for word: %s" % word)
    return text


def log(facility=config(key='database'), severity="INFO", verbosity=0, text=""):
    when = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    if config('verbosity') >= verbosity:
        print "%s %s : %s : %s : %s" % (when, config(key='database'), facility, severity, text)
    return


def sendsticker(chat_id=0, sticker="", text="", reply_to_message_id=""):
    url = "%s%s/sendSticker" % (config(key='url'), config(key='token'))
    message = "%s?chat_id=%s" % (url, chat_id)
    message = "%s&sticker=%s" % (message, sticker)
    if reply_to_message_id:
        message += "&reply_to_message_id=%s" % reply_to_message_id
    log(facility="sendsticker", verbosity=3, text="Sending sticker: %s" % text)
    return json.load(urllib.urlopen(message))


def stampy(chat_id="", karma=0):
    karma = "%s" % karma
    # Sticker definitions for each rank
    x00 = "BQADBAADYwAD17FYAAEidrCCUFH7AgI"
    x000 = "BQADBAADZQAD17FYAAEeeRNtkOWfBAI"
    x0000 = "BQADBAADZwAD17FYAAHHuNL2oLuShwI"
    x00000 = "BQADBAADaQAD17FYAAHzIBRZeY4uNAI"

    sticker = ""
    if karma[-5:] == "00000":
        sticker = x00000
    elif karma[-4:] == "0000":
        sticker = x0000
    elif karma[-3:] == "000":
        sticker = x000
    elif karma[-2:] == "00":
        sticker = x00

    text = "Sticker for %s karma points" % karma

    if sticker != "":
        sendsticker(chat_id=chat_id, sticker=sticker, text="%s" % text)
    return


def process():
    # Main code for processing the karma updates
    date = 0
    lastupdateid = 0
    log(facility="main", verbosity=0,
        text="Initial message at %s" % date)
    texto = ""
    error = False
    count = 0

    # Process each message available in URL and search for karma operators
    for message in getupdates():
        # Count messages in each batch
        count += 1
        update_id = message['update_id']

        try:
            chat_id = message['message']['chat']['id']
            chat_name = message['message']['chat']['title']
        except:
            chat_id = False
            chat_name = False

        try:
            texto = message['message']['text']
            message_id = int(message['message']['message_id'])
            date = int(float(message['message']['date']))
            who_gn = message['message']['from']['first_name']
            who_id = message['message']['from']['id']

        except:
            error = True
            who_id = False
            who_gn = False
            date = False
            message_id = False
            texto = False

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

        # Update stats on the message being processed
        if chat_id:
            updatestats(type="chat", id=chat_id, name=chat_name, date=date, count=0)
        if who_id:
            updatestats(type="user", id=who_id, name=who_gn, date=date, count=0)

        # Update last message id to later clear it from the server
        if update_id > lastupdateid:
            lastupdateid = update_id

        if not error:
            # Search for telegram commands
            telegramcommands(texto, chat_id, message_id, who_un)

            # Search for karma commands
            karmacommands(texto, chat_id, message_id)

            # Process each word in the line received to search for karma operators
            for word in texto.lower().split():
                if word[0] == "@":
                    # Remove @ from mentions for karma
                    word = word[1:]
                word = word.replace("'", '')
                # Unicode — is sometimes provided by telegram cli, using that also as comparision
                unidecrease = u"—"
                if word[-1:] == unidecrease:
                    word = word.replace(unidecrease, '--')

                log(facility="main", verbosity=9,
                    text="Processing word %s sent by id %s with username %s (%s %s)" % (
                        word, who_id, who_un, who_gn, who_ln))
                if len(word) >= 4:
                    # Determine karma change and apply it
                    change = 0
                    if "++" == word[-2:]:
                        log(facility="main", verbosity=1,
                            text="++ Found in %s at %s with id %s (%s), sent by id %s named %s (%s %s)" % (
                                word, chat_id, message_id, chat_name, who_id, who_un, who_gn, who_ln))
                        change = 1
                    if "--" == word[-2:]:
                        log(facility="main", verbosity=1,
                            text="-- Found in %s at %s with id %s (%s), sent by id %s named %s (%s %s)" % (
                                word, chat_id, message_id, chat_name, who_id, who_un, who_gn, who_ln))
                        change = -1
                    if change != 0:
                        # Remove last two characters from word (++ or --)
                        word = word[0:-2]
                        if getalias(word):
                            word = getalias(word)
                        karma = updatekarma(word=word, change=change)
                        if karma != 0:
                            # Karma has changed, report back
                            text = "%s now has %s karma points." % (word, karma)
                        else:
                            # New karma is 0
                            text = "%s now has no Karma and has been garbage collected." % word
                        # Send originating user for karma change a reply with
                        # the new value
                        sendmessage(chat_id=chat_id, text=text,
                                    reply_to_message_id=message_id)
                        stampy(chat_id=chat_id, karma=karma)

    log(facility="main", verbosity=0,
        text="Last processed message at: %s" % date)
    log(facility="main", verbosity=0,
        text="Last processed update_id : %s" % lastupdateid)
    log(facility="main", verbosity=0,
        text="Last processed text: %s" % texto)
    log(facility="main", verbosity=0,
        text="Number of messages in this batch: %s" % count)

    # clear updates (marking messages as read)
    clearupdates(offset=lastupdateid + 1)


# Main code

# Set database name in config
if options.database:
    setconfig(key='database', value=options.database)

if not config(key='sleep'):
    setconfig(key='sleep', value=10)

# Check if we've the token required to access or exit
if not config(key='token'):
    if options.token:
        token = options.token
        setconfig(key='token', value=token)
    else:
        log(facility="main", severity="ERROR", verbosity=0,
            text="Token required for operation, please check https://core.telegram.org/bots")
        sys.exit(1)
else:
    token = config(key='token')

# Check if we've URL defined on DB or on cli and store
if not config(key='url'):
    if options.url:
        setconfig(key='url', value=options.url)

# Check operation mode and call process as required
if options.daemon or config(key='daemon'):
    setconfig(key='daemon', value=True)
    log(facility="main", verbosity=0, text="Running in daemon mode")
    while 1 > 0:
        process()
        sleep(int(config(key='sleep')))
else:
    log(facility="main", verbosity=0,
        text="Running in one-shoot mode")
    process()

# Close database
if con:
    con.close()
