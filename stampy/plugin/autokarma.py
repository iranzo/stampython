#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing autokarma commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

from prettytable import from_db_cursor

import stampy.plugin.alias
import stampy.plugin.config
import stampy.plugin.karma
import stampy.stampy
from stampy.i18n import _
from stampy.i18n import _L


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """

    triggers = ["^/autok"]
    triggers.extend(getautokeywords(gid=False))

    return triggers


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    code = None
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower()[0:6] == "/autok":
            code = True
            autokcommands(message)
        autokarmawords(message)

    return code


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    if stampy.stampy.is_owner(message):
        commandtext = _("Use `/autok <key>=<value>` to autokarma <value> every time key is in the conversation. Multiple values for same <key> can be added\n\n")
        commandtext += _("Use `/autok delete <key>=<value>` to delete autokarma <value> for <key>\n\n")
        commandtext += _("Use `/autok list` to list autokarma <key> <value> pairs\n\n")
    return commandtext


def autokcommands(message):
    """
    Processes autok commands in the message texts
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger.debug(msg=_L("Command: %s by %s") % (texto, who_un))

    if stampy.stampy.is_owner_or_admin(message):
        logger.debug(msg=_L("Command: %s by Owner: %s") % (texto, who_un))
        try:
            command = texto.split(' ')[1]
        except:
            command = False
        try:
            word = texto.split(' ')[2]
        except:
            word = ""

        for case in stampy.stampy.Switch(command):
            if case('list'):
                text = listautok(word, gid=stampy.stampy.geteffectivegid(gid=chat_id))
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                break
            if case('delete'):
                word = texto.split(' ')[2]
                if "=" in word:
                    key = word.split('=')[0]
                    value = texto.split('=')[1:][0]
                    text = _("Deleting autokarma pair for `%s - %s`") % (key, value)
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                    deleteautok(key=key, value=value, gid=stampy.stampy.geteffectivegid(gid=chat_id))

            if case():
                word = texto.split(' ')[1]
                if "=" in word:
                    key = word.split('=')[0]
                    value = texto.split('=')[1:][0]
                    text = _("Setting autokarma for `%s` triggers `%s++`") % (key, value)
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                    createautok(word=key, value=value, gid=stampy.stampy.geteffectivegid(gid=chat_id))

    return


def getautok(key, gid=0):
    """
    Get autok for a key value pair in case it's defined
    :param gid: filter to group id
    :param key: key to search autok
    :return: list of values
    """

    logger = logging.getLogger(__name__)
    sql = "SELECT key,value FROM autokarma WHERE key='%s' AND gid='%s';" % (key, gid)
    cur = stampy.stampy.dbsql(sql)
    data = cur.fetchall()
    value = []
    for row in data:
        # Fill valid values
        value.append(row[1])

    logger.debug(msg="getautok: %s - %s for gid %s" % (key, value, gid))

    return value


def getautokeywords(gid=0):
    """
    Get autokeywords
    :return: List of autokeywords
    """

    logger = logging.getLogger(__name__)
    if gid is False:
        sql = "SELECT distinct key FROM autokarma;"
    else:
        sql = "SELECT distinct key FROM autokarma WHERE gid='%s';" % gid
    cur = stampy.stampy.dbsql(sql)
    data = cur.fetchall()
    value = []
    for row in data:
        # Fill valid values
        value.append(row[0])

    logger.debug(msg="getautokeywords: %s for gid %s" % (value, gid))

    return value


def createautok(word, value, gid=0):
    """
    Creates an autokarma trigger for a word
    :param gid: filter to group id
    :param word: word to use as base for the autokarma
    :param value: values to set as autokarma
    :return:
    """

    logger = logging.getLogger(__name__)
    if value in getautok(word):
        logger.error(msg=_L("createautok: autok pair %s - %s for gid %s already exists") % (word, value, gid))
    else:
        sql = "INSERT INTO autokarma(key, value, gid) VALUES('%s','%s', '%s');" % (word, value, gid)
        logger.debug(msg="createautok: %s=%s for gid %s" % (word, value, gid))
        stampy.stampy.dbsql(sql)
        return True
    return False


def deleteautok(key, value, gid=0):
    """
    Deletes a key - value pair from autokarma TABLE
    :param gid: filter to group id
    :param key:  key to delete
    :param value: value to delete
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "DELETE FROM autokarma WHERE key='%s' and value='%s' and gid='%s';" % (key, value, gid)
    logger.debug(msg="rmautok: %s=%s for gid %s" % (key, value, gid))
    stampy.stampy.dbsql(sql)
    return True


def listautok(word=False, gid=0):
    """
    Lists the autok pairs defined for a word, or all the autok
    :param gid: filter to group id
    :param word: word to return value for or everything
    :return: table with autok stored
    """

    logger = logging.getLogger(__name__)
    wordtext = ""

    if not word:
        sql = "select key,value from autokarma ORDER BY key ASC;"
    else:
        string = (word, gid)
        sql = "SELECT key,value FROM autokarma WHERE key='%s' AND gid='%s' ORDER by key ASC;" % string
        wordtext = _("for word %s for gid %s") % (word, gid)

    cur = stampy.stampy.dbsql(sql)

    try:
        # Get value from SQL query
        text = _("Defined autokarma triggers %s:\n") % wordtext
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())

    except:
        # Value didn't exist before
        text = _("%s has no trigger autokarma") % word

    logger.debug(msg=_L("Returning autokarma %s for word %s") % (text, word))
    return text


def autokarmawords(message):
    """
    Finds commands affecting autokarma in messages
    :param message: message to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)
    text_to_process = msgdetail["text"].lower()
    chat_id = msgdetail['chat_id']
    gid = stampy.stampy.geteffectivegid(gid=chat_id)

    wordadd = []

    keywords = getautokeywords(gid=gid)
    for autok in keywords:
        if autok in text_to_process:
            # If trigger word is there, add the triggered action
            for word in getautok(key=autok, gid=gid):
                wordadd.append(word + "++")

    if wordadd:
        # Reduce text in message to just the words we encountered to optimize
        msgdetail["text"] = " ".join(wordadd)
        logger.debug(msg=_L("Autokarma words %s encountered for processing") % msgdetail["text"])
        stampy.plugin.karma.karmaprocess(msgdetail)

    return
