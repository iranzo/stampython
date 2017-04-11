#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing quote commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import datetime
import logging
import time

import stampy.stampy
import stampy.plugin.config
from stampy.i18n import translate
_ = translate.ugettext


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    triggers = ["^/quote"]
    return triggers


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower() == "/quote":
            quotecommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = _("Use `/quote add <id> <text>` to add a quote for that username\n")
    commandtext += _("Use `/quote <id>` to get a random quote from that username\n\n")
    if stampy.plugin.config.config(key='owner') == stampy.stampy.getmsgdetail(message)["who_un"]:
        commandtext += _("Use `/quote del <quoteid>` to remove a quote\n\n")
    return commandtext


def quotecommands(message):
    """
    Searches for commands related to quotes
    :param message: message to process
    :return:
    """

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger = logging.getLogger(__name__)
    logger.debug(msg="Command: %s by %s" % (texto, who_un))

    # We might be have been given no command, just /quote
    try:
        command = texto.split(' ')[1]
    except:
        command = False

    for case in stampy.stampy.Switch(command):
        # cur.execute('CREATE TABLE quote(id AUTOINCREMENT, name TEXT,
        # date TEXT, text TEXT;')
        if case('add'):
            who_quote = texto.split(' ')[2]
            date = time.time()
            quote = str.join(" ", texto.split(' ')[3:])
            result = addquote(username=who_quote, date=date, text=quote)
            text = _("Quote `%s` added") % result
            stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                      reply_to_message_id=message_id,
                                      disable_web_page_preview=True,
                                      parse_mode="Markdown")
            break
        if case('del'):
            if who_un == stampy.plugin.config.config(key='owner'):
                id_todel = texto.split(' ')[2]
                text = _("Deleting quote id `%s`") % id_todel
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
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
                text = '`%s` -- `@%s`, %s (id %s)' % (
                       quote, username, datefor, quoteid)
            except:
                if nick:
                    text = _("No quote recorded for `%s`") % nick
                else:
                    text = _("No quote found")
            stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                      reply_to_message_id=message_id,
                                      disable_web_page_preview=True,
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
        sql = "SELECT id,username,date,text FROM quote WHERE username='%s' ORDER BY RANDOM() LIMIT 1;" % string
    else:
        sql = "SELECT id,username,date,text FROM quote ORDER BY RANDOM() LIMIT 1;"
    cur = stampy.stampy.dbsql(sql)
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
    sql = "INSERT INTO quote(username, date, text) VALUES('%s','%s', '%s');" % (
          username, date, text)
    cur = stampy.stampy.dbsql(sql)
    logger.debug(msg=_("createquote: %s=%s on %s") % (username, text, date))
    # Retrieve last id
    sql = "select last_insert_rowid();"
    cur = stampy.stampy.dbsql(sql)
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
    return stampy.stampy.dbsql(sql)
