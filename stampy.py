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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
# GNU General Public License for more details.

import datetime
import json
import logging
import optparse
import sqlite3 as lite
import string
import sys
import time
import urllib
from time import sleep

from prettytable import from_db_cursor

description = """
Stampy is a script for controlling Karma via Telegram.org bot api

"""

# Option parsing
p = optparse.OptionParser("stampy.py [arguments]", description=description)
p.add_option("-t", "--token", dest="token",
             help="API token for bot access to messages", default=False)
p.add_option("-b", "--database", dest="database",
             help="database file for storing karma and last processed message",
             default="stampy.db")
p.add_option('-v', "--verbosity", dest="verbosity",
             help="Set verbosity level for messages while running/logging", default=0, type='choice',
             choices=["info", "debug", "warn", "critical"])
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
    """
    Defines a class that can be used easily as traditional switch commands
    """

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


def createdb():
    """
    Create database if it doesn't exist
    :return:
    """
    cur.execute('CREATE TABLE karma(word TEXT, value INT);')
    cur.execute('CREATE TABLE alias(key TEXT, value TEXT);')
    cur.execute('CREATE TABLE config(key TEXT, value TEXT);')
    cur.execute('CREATE TABLE stats(type TEXT, id INT, name TEXT, date TEXT, count INT);')
    cur.execute('CREATE TABLE quote(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, date TEXT, text TEXT);')
    return


# Initialize database access
con = False
try:
    con = lite.connect(options.database)
    cur = con.cursor()
    cur.execute("SELECT * FROM config WHERE key='token';")
    data = cur.fetchone()

except lite.Error, e:
    createdb()
    print "Error %s:" % e.args[0]
    print "DB has been created, please, execute again"
    sys.exit(1)


# Database initialized

# Function definition
def dbsql(sql=False):
    """
    Performs SQL operation on database
    :param sql: sql command to execute
    :return:
    """
    logger = logging.getLogger(__name__)
    if sql:
        try:
            cur.execute(sql)
            con.commit()
            worked = True
        except:
            worked = False
    if not worked:
        logger.critical(msg="Error on SQL execution: %s" % sql)

    return worked


def sendmessage(chat_id=0, text="", reply_to_message_id=False, disable_web_page_preview=True, parse_mode=False,
                extra=False):
    """
    Sends a message to a chat
    :param chat_id: chat_id to receive the message
    :param text: message text
    :param reply_to_message_id: message_id to reply
    :param disable_web_page_preview: do not expand links to include page preview
    :param parse_mode: use specific format (markdown, html)
    :param extra: extra parameters to send (for future functions like keyboard_markup)
    :return:
    """

    logger = logging.getLogger(__name__)
    url = "%s%s/sendMessage" % (config(key="url"), config(key='token'))
    lines = text.split("\n")
    maxlines = 15
    if len(lines) > maxlines:
        # message might be too big for single message (max 4K)
        if "```" in text:
            markdown = True
        else:
            markdown = False

        texto = string.join(lines[0:maxlines], "\n")
        if markdown:
            texto = "%s```" % texto

        # Send first batch
        sendmessage(chat_id=chat_id, text=texto, reply_to_message_id=reply_to_message_id,
                    disable_web_page_preview=disable_web_page_preview, parse_mode=parse_mode, extra=extra)
        # Send remaining batch
        texto = string.join(lines[maxlines:], "\n")
        if markdown:
            texto = "```%s" % texto
        sendmessage(chat_id=chat_id, text=texto, reply_to_message_id=False,
                    disable_web_page_preview=disable_web_page_preview, parse_mode=parse_mode, extra=extra)
        return

    message = "%s?chat_id=%s&text=%s" % (url, chat_id,
                                         urllib.quote_plus(text.encode('utf-8'))
                                         )
    if reply_to_message_id:
        message += "&reply_to_message_id=%s" % reply_to_message_id
    if disable_web_page_preview:
        message += "&disable_web_page_preview=1"
    if parse_mode:
        message += "&parse_mode=%s" % parse_mode
    if extra:
        message += "&%s" % extra

    code = False
    while not code:
        result = json.load(urllib.urlopen(message))
        code = result['ok']
        logger.error(msg="ERROR sending message: Code: %s : Text: %s" % (code, result))
        sleep(1)
    logger.debug(msg="Sending message: Code: %s : Text: %s" % (code, text))
    return


def getupdates(offset=0, limit=100):
    """
    Gets updates (new messages from server)
    :param offset: last update id
    :param limit: maximum number of messages to gather
    :return: returns the items obtained
    """

    logger = logging.getLogger(__name__)
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
        logger.info(msg="Getting updates and returning: %s" % item)
        yield item


def clearupdates(offset):
    """
    Marks updates as already processed so they are removed by API
    :param offset:
    :return:
    """

    logger = logging.getLogger(__name__)
    url = "%s%s/getUpdates" % (config(key='url'), config(key='token'))
    message = "%s?" % url
    message += "offset=%s&" % offset
    try:
        result = json.load(urllib.urlopen(message))
    except:
        result = False
    logger.info(msg="Clearing messages")
    return result


def updatekarma(word=False, change=0):
    """
    Updates karma for a word
    :param word:  Word to update
    :param change:  Change in karma
    :return:
    """

    logger = logging.getLogger(__name__)
    value = getkarma(word=word)
    return putkarma(word, value + change)


def getkarma(word):
    """
    Gets karma for a word
    :param word: word to get karma for
    :return: karma of given word
    """

    logger = logging.getLogger(__name__)
    string = (word,)
    sql = "SELECT * FROM karma WHERE word='%s';" % string
    dbsql(sql)
    value = cur.fetchone()

    try:
        # Get value from SQL query
        value = value[1]

    except:
        # Value didn't exist before, return 0
        value = 0

    return value


def config(key):
    """
    Gets configuration from database for a given key
    :param key: key to get configuration for
    :return: value in database for that key
    """

    logger = logging.getLogger(__name__)
    string = (key,)
    sql = "SELECT * FROM config WHERE key='%s';" % string
    dbsql(sql)
    value = cur.fetchone()

    try:
        # Get value from SQL query
        value = value[1]

    except:
        # Value didn't exist before, return 0
        value = False

    return value


def saveconfig(key, value):
    """
    Saves configuration for a given key to a defined value
    :param key: key to save
    :param value: value to store
    :return:
    """

    logger = logging.getLogger(__name__)
    if value:
        sql = "UPDATE config SET value = '%s' WHERE key = '%s';" % (value, key)
        dbsql(sql)
    return value


def createkarma(word):
    """
    Creates a new word in karma database
    :param word: word to create
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "INSERT INTO karma VALUES('%s',0);" % word
    return dbsql(sql)


def putkarma(word, value):
    """
    Updates value of karma for a word
    :param word: Word to update
    :param value: Value of karma to set
    :return:
    """

    logger = logging.getLogger(__name__)
    if getkarma(word) == 0:
        createkarma(word)
    if value != 0:
        sql = "UPDATE karma SET value = '%s' WHERE word = '%s';" % (value, word)
    else:
        sql = "DELETE FROM karma WHERE  word = '%s';" % word
    dbsql(sql)
    return value


def getstats(type=False, id=0, name=False, date=False, count=0):
    """
    Gets statistics for specified element
    :param type: chat or user type to query
    :param id: identifier for user or chat
    :param name: full name
    :param date: date
    :param count: number of messages
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "SELECT * FROM stats WHERE id='%s' AND type='%s';" % (id, type)
    dbsql(sql)
    try:
        value = cur.fetchone()
    except:
        value = False

    if value:
        (type, id, name, date, count) = value
    if not type or not id or not name or not date:
        value = False
    if not count:
        count = 0
    log.debug(msg="values: type:%s, id:%s, name:%s, date:%s, count:%s" % (type, id, name, date, count))

    return value


def updatestats(type=False, id=0, name=False, date=False):
    """
    Updates count stats for a given type
    :param type: user or chat
    :param id: ID to update
    :param name: name of the chat of user
    :param date: date of the update
    :return:
    """

    logger = logging.getLogger(__name__)
    try:
        value = getstats(type=type, id=id)
        count = value[4] + 1
        type = type
        id = id
        name = name
    except:
        value = False
        count = 0

    # Asume value doesn't exist, then set to update if it does
    sql = "INSERT INTO stats VALUES('%s', '%s', '%s', '%s', '%s');" % (type, id, name, date, count)
    if value:
        sql = "UPDATE stats SET type='%s',name='%s',date='%s',count='%s' WHERE id='%s';" % (
            type, name, date, count, id)
    logger.debug(msg="values: type:%s, id:%s, name:%s, date:%s, count:%s" % (type, id, name, date, count))

    if id:
        try:
            dbsql(sql)
        except:
            print "ERROR on updatestats"
    return


def telegramcommands(texto, chat_id, message_id, who_un):
    """
    Processes telegram commands in message texts (/help, etc)
    :param texto: text from the update
    :param chat_id:  chat to answer to
    :param message_id: message to reply to
    :param who_un: username of user providing the command
    :return:
    """

    logger = logging.getLogger(__name__)

    # Process lines for commands in the first word of the line (Telegram)
    word = texto.split()[0]
    if "@" in word:
        # If the message is directed as /help@bot, remove that part
        word = word.split("@")[0]

    commandtext = False
    for case in Switch(word):
        if case('/help'):
            commandtext = "To use this bot use `word++` or `word--` to increment or decrement karma, a new message will be sent providing the new total\n\n"
            commandtext += "Use `rank word` or `rank` to get value for actual word or top 10 rankings\n"
            commandtext += "Use `srank word` to search for similar words already ranked\n\n"
            commandtext += "Use `/quote add <id> <text>` to add a quote for that username\n"
            commandtext += "Use `/quote <id>` to get a random quote from that username\n\n"
            if config(key='owner') == who_un:
                commandtext += "Use `/quote del <quoteid>` to remove a quote\n\n"
                commandtext += "Use `/alias <key>=<value>` to assign an alias for karma\n"
                commandtext += "Use `/alias list` to list aliases\n"
                commandtext += "Use `/alias delete <key>` to remove an alias\n\n"
                commandtext += "Use `/stats <user|chat>` to get stats on last usage\n\n"
                commandtext += "Use `/config show` to get a list of defined config settings\n"
                commandtext += "Use `/config set <key>=<value>` to define a value for key\n"
                commandtext += "Use `/config delete <key>` to delete key\n\n"
            commandtext += "Learn more about this bot in [https://github.com/iranzo/stampython](https://github.com/iranzo/stampython)"
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
        if case('/quote'):
            quotecommands(texto, chat_id, message_id, who_un)
            break
        if case('/stats'):
            statscommands(texto, chat_id, message_id, who_un)
            break
        if case():
            commandtext = False

    # If any of above commands did match, send command
    if commandtext:
        sendmessage(chat_id=chat_id, text=commandtext, reply_to_message_id=message_id, parse_mode="Markdown")
        logger.debug(msg="Command: %s" % word)
    return


def getalias(word):
    """
    Get alias for a word in case it's defined
    :param word: word to search alias
    :return: alias if existing or word if not
    """

    logger = logging.getLogger(__name__)
    string = (word,)
    sql = "SELECT * FROM alias WHERE key='%s';" % string
    dbsql(sql)
    value = cur.fetchone()
    logger.debug(msg="getalias: %s" % word)

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
    """
    Creates an alias for a word
    :param word: word to use as base for the alias
    :param value: values to set as alias
    :return:
    """

    logger = logging.getLogger(__name__)
    if getalias(value) == word:
        logger.error(msg="createalias: circular reference %s=%s" % (word, value))
    else:
        if not getalias(word) or getalias(word) == word:
            sql = "INSERT INTO alias VALUES('%s','%s');" % (word, value)
            logger.debug(msg="createalias: %s=%s" % (word, value))
            return dbsql(sql)
    return False


def deletealias(word):
    """
    Deletes a word from the alias database
    :param word:  word to delete
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "DELETE FROM alias WHERE key='%s';" % word
    logger.debug(msg="rmalias: %s" % word)
    return dbsql(sql)


def listalias(word=False):
    """
    Lists the alias defined for a word, or all the aliases
    :param word: word to return value for or everything
    :return: table with alias stored
    """

    logger = logging.getLogger(__name__)
    if word:
        # if word is provided, return the alias for that word
        string = (word,)
        sql = "SELECT * FROM alias WHERE key='%s' ORDER by key ASC;" % string
        dbsql(sql)
        value = cur.fetchone()

        try:
            # Get value from SQL query
            value = value[1]

        except:
            # Value didn't exist before, return 0 value
            value = 0
        text = "%s has an alias %s" % (word, value)

    else:
        sql = "select * from alias ORDER BY key ASC;"
        dbsql(sql)
        text = "Defined aliases:\n"
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg="Returning aliases %s for word %s" % (text, word))
    return text


def setconfig(key, value):
    """
    Sets a config parameter in database
    :param key: key to update
    :param value: value to store
    :return:
    """

    logger = logging.getLogger(__name__)
    if config(key=key):
        deleteconfig(key)
    sql = "INSERT INTO config VALUES('%s','%s');" % (key, value)
    logger.debug(msg="setconfig: %s=%s" % (key, value))
    return dbsql(sql)


def deleteconfig(word):
    """
    Deletes a config parameter in database
    :param word: key to remove
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "DELETE FROM config WHERE key='%s';" % word
    logger.debug(msg="rmconfig: %s" % word)
    return dbsql(sql)


def showconfig(key=False):
    """
    Shows configuration in database for a key or all values
    :param key: key to return value for
    :return: Value stored
    """
    logger = logging.getLogger(__name__)
    if key:
        # if word is provided, return the config for that key
        string = (key,)
        sql = "SELECT * FROM config WHERE key='%s';" % string
        dbsql(sql)
        value = cur.fetchone()

        try:
            # Get value from SQL query
            value = value[1]

        except:
            # Value didn't exist before, return 0 value
            value = 0
        text = "%s has a value of %s" % (key, value)

    else:
        sql = "select * from config ORDER BY key ASC;"
        dbsql(sql)
        text = "Defined configurations:\n"
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg="Returning config %s for key %s" % (text, key))
    return text


def aliascommands(texto, chat_id, message_id, who_un):
    """
    Processes alias commands in the message texts
    :param texto: text of the message
    :param chat_id:  chat_ID
    :param message_id: message_ID to reply to
    :param who_un: username sending the request
    :return:
    """

    logger = logging.getLogger(__name__)
    logger.debug(msg="Command: %s by %s" % (texto, who_un))
    if who_un == config('owner'):
        logger.debug(msg="Command: %s by Owner: %s" % (texto, who_un))
        try:
            command = texto.split(' ')[1]
        except:
            command = False
        try:
            word = texto.split(' ')[2]
        except:
            word = ""

        for case in Switch(command):
            if case('list'):
                text = listalias(word)
                sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True,
                            parse_mode="Markdown")
                break
            if case('delete'):
                key = word
                text = "Deleting alias for `%s`" % key
                sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True,
                            parse_mode="Markdown")
                deletealias(word=key)
                break
            if case():
                word = texto.split(' ')[1]
                if "=" in word:
                    key = word.split('=')[0]
                    value = texto.split('=')[1:][0]
                    text = "Setting alias for `%s` to `%s`" % (key, value)
                    sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id,
                                disable_web_page_preview=True, parse_mode="Markdown")
                    # Removing duplicates on karma DB and add the previous values
                    old = getkarma(key)
                    updatekarma(word=key, change=-old)
                    updatekarma(word=value, change=old)
                    createalias(word=key, value=value)

    return


def quotecommands(texto, chat_id, message_id, who_un):
    """
    Searches for commands related to quotes
    :param texto: text of the message
    :param chat_id:  chat_ID
    :param message_id: message_ID to reply to
    :param who_un: username sending the request
    :return:
    """

    logger = logging.getLogger(__name__)
    logger.debug(msg="Command: %s by %s" % (texto, who_un))

    # We might be have been given no command, just /quote
    try:
        command = texto.split(' ')[1]
    except:
        command = False

    for case in Switch(command):
        # cur.execute('CREATE TABLE quote(id AUTOINCREMENT, name TEXT, date TEXT, text TEXT;')
        if case('add'):
            who_quote = texto.split(' ')[2]
            date = time.time()
            quote = str.join(" ", texto.split(' ')[3:])
            result = addquote(username=who_quote, date=date, text=quote)
            text = "Quote `%s` added" % result
            sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True,
                        parse_mode="Markdown")
            break
        if case('del'):
            if who_un == config(key='owner'):
                id_todel = texto.split(' ')[2]
                text = "Deleting quote id `%s`" % id_todel
                sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id,
                            disable_web_page_preview=True, parse_mode="Markdown")
                deletequote(id=id_todel)
            break
        if case():
            # We're just given the nick (or not), so find quote for it
            try:
                nick = texto.split(' ')[1]
            except:
                nick = False
            try:
                (quoteid, username, date, quote) = getquote(username=nick)
                datefor = datetime.datetime.fromtimestamp(float(date)).strftime('%Y-%m-%d %H:%M:%S')
                text = '`%s` -- `@%s`, %s (id %s)' % (quote, username, datefor, quoteid)
            except:
                if nick:
                    text = "No quote recorded for `%s`" % nick
                else:
                    text = "No quote found"
            sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True,
                        parse_mode="Markdown")

    return


def getquote(username=False):
    """
    Gets quote for a specified username or a random one
    :param username: username to get quote for
    :return: text for the quote or empty
    """

    logger = logging.getLogger(__name__)
    if username:
        string = (username,)
        sql = "SELECT * FROM quote WHERE username='%s' ORDER BY RANDOM() LIMIT 1;" % string
    else:
        sql = "SELECT * FROM quote ORDER BY RANDOM() LIMIT 1;"
    dbsql(sql)
    value = cur.fetchone()
    logger.debug(msg="getquote: %s" % username)
    try:
        # Get value from SQL query
        (quoteid, username, date, quote) = value

    except:
        # Value didn't exist before, return 0
        quoteid = False
        username = False
        date = False
        quote = False

    if quoteid:
        return quoteid, username, date, quote

    return False

def addquote(username=False, date=False, text=False):
    """
    Adds a quote for a specified username
    :param username: username to store quote for
    :param date: date when quote was added
    :param text: text of the quote
    :return: returns quote ID entry in database
    """

    logger = logging.getLogger(__name__)
    sql = "INSERT INTO quote(username, date, text) VALUES('%s','%s', '%s');" % (username, date, text)
    dbsql(sql)
    logger.debug(msg="createquote: %s=%s on %s" % (username, text, date))
    # Retrieve last id
    sql = "select last_insert_rowid();"
    dbsql(sql)
    lastrowid = cur.fetchone()[0]
    return lastrowid


def deletequote(id=False):
    """
    Deletes quote from the database
    :param id: ID of the quote to remove
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "DELETE FROM quote WHERE id='%s';" % id
    logger.debug(msg="deletequote: %s" % id)
    return dbsql(sql)


def configcommands(texto, chat_id, message_id, who_un):
    """
    Processes configuration commands in the message
    :param texto: text of the message
    :param chat_id: chat_id originating the request
    :param message_id: message_id to reply to
    :param who_un: username of the originator
    :return:
    """

    logger = logging.getLogger(__name__)

    # Only users defined as 'owner' can perform commands
    if who_un == config('owner'):
        logger.debug(msg="Command: %s by %s" % (texto, who_un))
        try:
            command = texto.split(' ')[1]
        except:
            command = False

        try:
            word = texto.split(' ')[2]
        except:
            word = ""

        for case in Switch(command):
            if case('show'):
                text = showconfig(word)
                sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True,
                            parse_mode="Markdown")
                break
            if case('delete'):
                key = word
                text = "Deleting config for `%s`" % key
                sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True,
                            parse_mode="Markdown")
                deleteconfig(word=key)
                break
            if case('set'):
                word = texto.split(' ')[2]
                if "=" in word:
                    key = word.split('=')[0]
                    value = word.split('=')[1]
                    setconfig(key=key, value=value)
                    text = "Setting config for `%s` to `%s`" % (key, value)
                    sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id,
                                disable_web_page_preview=True, parse_mode="Markdown")
                break
            if case():
                break

    return


def showstats(type=False):
    """
    Shows stats for defined type or all if missing
    :param type: user or chat or empy for combined
    :return: table with the results
    """
    logger = logging.getLogger(__name__)
    if type:
        sql = "select * from stats WHERE type='%s' ORDER BY count DESC" % type
    else:
        sql = "select * from stats ORDER BY count DESC"
    dbsql(sql)
    table = from_db_cursor(cur)
    text = "Defined stats:\n"
    text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg="Returning stats %s" % text)
    return text


def statscommands(texto, chat_id, message_id, who_un):
    """
    Processes stats commands in the messages
    :param texto: message to process
    :param chat_id: Chat_ID from the request
    :param message_id: message_id to reply to
    :param who_un: originating user for the request
    :return:
    """

    logger = logging.getLogger(__name__)
    if who_un == config('owner'):
        logger.debug(msg="Owner Stat: %s by %s" % (texto, who_un))
        try:
            command = texto.split(' ')[1]
        except:
            command = False

        try:
            key = texto.split(' ')[2]
        except:
            key = ""

        for case in Switch(command):
            if case('show'):
                text = showstats(key)
                sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True,
                            parse_mode="Markdown")
                break
            if case():
                break

    return


def karmacommands(texto, chat_id, message_id):
    """
    Finds for commands affecting karma in messages
    :param texto: message to analyze
    :param chat_id: chat_id originating the request
    :param message_id: message_id to reply to
    :return:
    """

    logger = logging.getLogger(__name__)
    # Process lines for commands in the first word of the line (Telegram commands)
    word = texto.split()[0]
    commandtext = False

    # Check first word for commands
    for case in Switch(word):
        if case('rank'):
            try:
                word = texto.split()[1]
            except:
                word = False
            commandtext = rank(word)
            break
        if case('srank'):
            try:
                word = texto.split()[1]
            except:
                word = False
            commandtext = srank(word)
            break
        if case():
            commandtext = False

    # If any of above cases did a match, send command
    if commandtext:
        sendmessage(chat_id=chat_id, text=commandtext,
                    reply_to_message_id=message_id, parse_mode="Markdown")
        logger.debug(msg="karmacommand:  %s" % word)
    return


def rank(word=False):
    """
    Outputs rank for word or top 10
    :param word: word to return rank for
    :return:
    """

    logger = logging.getLogger(__name__)
    if getalias(word):
        word = getalias(word)
    if word:
        # if word is provided, return the rank value for that word
        string = (word,)
        sql = "SELECT * FROM karma WHERE word='%s';" % string
        dbsql(sql)
        value = cur.fetchone()

        try:
            # Get value from SQL query
            value = value[1]

        except:
            # Value didn't exist before, return 0 value
            value = 0
        text = "`%s` has `%s` karma points." % (word, value)

    else:
        # if word is not provided, return top 10 words with top karma
        sql = "select * from karma ORDER BY value DESC LIMIT 10;"

        text = "Global rankings:\n"
        dbsql(sql)
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg="Returning karma %s for word %s" % (text, word))
    return text


def srank(word=False):
    """
    Search for rank for word
    :param word: word to search in database
    :return: table with the values for srank
    """
    logger = logging.getLogger(__name__)
    if getalias(word):
        word = getalias(word)
    text = ""
    if word is False:
        # If no word is provided to srank, call rank instead
        text = rank(word)
    else:
        string = "%" + word + "%"
        sql = "SELECT * FROM karma WHERE word LIKE '%s' LIMIT 10;" % string
        dbsql(sql)
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg="Returning srank for word: %s" % word)
    return text


def sendsticker(chat_id=0, sticker="", text="", reply_to_message_id=""):
    """
    Sends a sticker to chat_id as a reply to a message received
    :param chat_id: ID of the chat
    :param sticker: Sticker identification
    :param text: Additional text
    :param reply_to_message_id:
    :return:
    """

    logger = logging.getLogger(__name__)
    url = "%s%s/sendSticker" % (config(key='url'), config(key='token'))
    message = "%s?chat_id=%s" % (url, chat_id)
    message = "%s&sticker=%s" % (message, sticker)
    if reply_to_message_id:
        message += "&reply_to_message_id=%s" % reply_to_message_id
    logger.debug(msg="Sending sticker: %s" % text)
    return json.load(urllib.urlopen(message))


def stampy(chat_id="", karma=0):
    """
    Returns a sticker for big karma values
    :param chat_id:
    :param karma:
    :return:
    """

    logger = logging.getLogger(__name__)
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
    """
    This function processes the updates in the Updates URL at Telgram for finding commands, karma changes, config, etc
    """

    logger = logging.getLogger(__name__)

    # check if Log level has changed
    loglevel()

    # Main code for processing the karma updates
    date = 0
    lastupdateid = 0
    logger.info(msg="Initial message at %s" % date)
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
        except:
            chat_id = False

        try:
            chat_name = message['message']['chat']['title']
        except:
            chat_name = False

        try:
            texto = message['message']['text']
            message_id = int(message['message']['message_id'])
            date = int(float(message['message']['date']))
            datefor = datetime.datetime.fromtimestamp(float(date)).strftime('%Y-%m-%d %H:%M:%S')
            who_gn = message['message']['from']['first_name']
            who_id = message['message']['from']['id']

        except:
            error = True
            who_id = False
            who_gn = False
            date = False
            datefor = False
            message_id = False
            texto = False

        try:
            who_ln = message['message']['from']['last_name']
        except:
            who_ln = False

        # Some user might not have username defined so this
        # was failing and message was ignored
        try:
            who_un = message['message']['from']['username']

        except:
            who_un = False

        # Update stats on the message being processed
        if chat_id and chat_name:
            updatestats(type="chat", id=chat_id, name=chat_name, date=datefor)

        name = "%s %s (@%s)" % (who_gn, who_ln, who_un)

        if who_ln:
            updatestats(type="user", id=who_id, name=name, date=datefor)

        # Update last message id to later clear it from the server
        if update_id > lastupdateid:
            lastupdateid = update_id

        # Write the line for debug
        messageline = "TEXT: %s : %s : %s" % (chat_name, name, texto)
        logger.debug(msg=messageline)

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

                logger.debug(msg="Processing word %s sent by id %s with username %s (%s %s)" % (
                    word, who_id, who_un, who_gn, who_ln))
                if len(word) >= 4:
                    # Determine karma change and apply it
                    change = 0
                    if "++" == word[-2:]:
                        logger.debug(msg="++ Found in %s at %s with id %s (%s), sent by id %s named %s (%s %s)" % (
                            word, chat_id, message_id, chat_name, who_id, who_un, who_gn, who_ln))
                        change = 1
                    if "--" == word[-2:]:
                        logger.debug(msg="-- Found in %s at %s with id %s (%s), sent by id %s named %s (%s %s)" % (
                            word, chat_id, message_id, chat_name, who_id, who_un, who_gn, who_ln))
                        change = -1
                    if change != 0:
                        # Remove last two characters from word (++ or --)
                        word = word[0:-2]
                        if getalias(word):
                            word = getalias(word).split(" ")
                        for item in word:
                            if getalias(item):
                                item = getalias(item)
                            karma = updatekarma(word=item, change=change)
                            if karma != 0:
                                # Karma has changed, report back
                                text = "`%s` now has `%s` karma points." % (item, karma)
                            else:
                                # New karma is 0
                                text = "`%s` now has no Karma and has been garbage collected." % item
                            # Send originating user for karma change a reply with
                            # the new value
                            sendmessage(chat_id=chat_id, text=text,
                                        reply_to_message_id=message_id, parse_mode="Markdown")
                            stampy(chat_id=chat_id, karma=karma)

    logger.info(msg="Last processed message at: %s" % date)
    logger.debug(msg="Last processed update_id : %s" % lastupdateid)
    logger.debug(msg="Last processed text: %s" % texto)
    logger.info(msg="Number of messages in this batch: %s" % count)

    # clear updates (marking messages as read)
    clearupdates(offset=lastupdateid + 1)


def loglevel():
    """
    This functions stores or sets the proper log level based on the database configuration
    """

    logger = logging.getLogger(__name__)

    for case in Switch(config(key="verbosity").lower()):
        # choices=["info", "debug", "warn", "critical"])
        if case('debug'):
            level = logging.DEBUG
            break
        if case('critical'):
            level = logging.CRITICAL
            break
        if case('warn'):
            level = logging.WARN
            break
        if case('info'):
            level = logging.INFO
            break
        if case():
            # Default to DEBUG log level
            level = logging.DEBUG

    # If logging level has changed, redefine in logger, database and send message
    if logging.getLevelName(logger.level).lower() != config(key="verbosity"):
        logger.setLevel(level)
        logger.info(msg="Logging level set to %s" % config(key="verbosity"))
        setconfig(key="verbosity", value=logging.getLevelName(logger.level).lower())
    else:
        logger.debug(msg="Log level didn't changed from %s" % config(key="verbosity").lower())


def conflogging():
    """
    This function configures the logging handlers for console and file
    """

    logger = logging.getLogger(__name__)

    # Define logging settings
    if not config(key="verbosity"):
        if not options.verbosity:
            # If we don't have defined command line value and it's not stored, use DEBUG
            setconfig(key="verbosity", value="DEBUG")
        else:
            setconfig(key="verbosity", value=options.verbosity)

    loglevel()

    # create formatter
    formatter = logging.Formatter('%(asctime)s : %(name)s : %(funcName)s(%(lineno)d) : %(levelname)s : %(message)s')

    # create console handler and set level to debug
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # create file logger
    filename = '%s.log' % config(key='database').split(".")[0]

    file = logging.FileHandler(filename)
    file.setLevel(logging.DEBUG)
    file.setFormatter(formatter)
    logger.addHandler(file)

    return


def main():
    """
    Main code for the bot
    """

    # Main code
    logger = logging.getLogger(__name__)

    conflogging()

    # Set database name in config
    if options.database:
        setconfig(key='database', value=options.database)

    logger.info(msg="Started execution")

    if not config(key='sleep'):
        setconfig(key='sleep', value=10)

    # Check if we've the token required to access or exit
    if not config(key='token'):
        if options.token:
            token = options.token
            setconfig(key='token', value=token)
        else:
            logger.critical(msg="Token required for operation, please check https://core.telegram.org/bots")
            sys.exit(1)
    else:
        token = config(key='token')

    # Check if we've URL defined on DB or on cli and store
    if not config(key='url'):
        if options.url:
            setconfig(key='url', value=options.url)

    # Check if we've owner defined in DB or on cli and store
    if not config(key='owner'):
        if options.owner:
            setconfig(key='owner', value=options.owner)

    # Check operation mode and call process as required
    if options.daemon or config(key='daemon'):
        setconfig(key='daemon', value=True)
        logger.info(msg="Running in daemon mode")
        while 1 > 0:
            process()
            sleep(int(config(key='sleep')))
    else:
        logger.info(msg="Running in one-shoot mode")
        process()

    # Close database
    if con:
        con.close()
    logger.info(msg="Stopped execution")
    logging.shutdown()
    sys.exit(0)


if __name__ == "__main__":
    # Set name to the database being used to allow multibot execution
    __name__ = config(key="database").split(".")[0]
    main()
