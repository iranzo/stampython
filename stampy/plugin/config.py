#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing config commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

from prettytable import from_db_cursor

import stampy.stampy


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    return "/config"


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower() == "/config":
            configcommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    if config(key='owner') == stampy.stampy.getmsgdetail(message)["who_un"]:
        commandtext = "Use `/config show` to get a list " \
                      "of defined config settings\n"
        commandtext += "Use `/config set <key>=<value>` to define" \
                       " a value for key\n"
        commandtext += "Use `/config delete <key>` to delete key\n\n"
    return commandtext


def configcommands(message):
    """
    Processes configuration commands in the message
    :param message: message to process
    :return:
    """
    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

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

        for case in stampy.stampy.Switch(command):
            if case('show'):
                text = showconfig(word)
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                break
            if case('delete'):
                key = word
                text = "Deleting config for `%s`" % key
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                deleteconfig(word=key)
                break
            if case('set'):
                word = " ".join(texto.split(' ')[2:])
                if "=" in word:
                    key = word.split('=')[0]
                    value = word.split('=')[1]
                    setconfig(key=key, value=value)
                    text = "Setting config for `%s` to `%s`" % (key, value)
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                break
            if case():
                break

    return


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
        cur = stampy.stampy.dbsql(sql)
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
        cur = stampy.stampy.dbsql(sql)
        text = "Defined configurations:\n"
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg="Returning config %s for key %s" % (text, key))
    return text


def config(key, default=False):
    """
    Gets configuration from database for a given key
    :param key: key to get configuration for
    :param default: value to return for key if not define or False
    :return: value in database for that key
    """

    # logger = logging.getLogger(__name__)
    string = (key,)
    sql = "SELECT * FROM config WHERE key='%s';" % string
    cur = stampy.stampy.dbsql(sql)
    value = cur.fetchone()

    try:
        # Get value from SQL query
        value = value[1]

    except:
        # Value didn't exist before, return default or False
        value = default

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
        stampy.stampy.dbsql(sql)
        logger.debug(msg="Updating config for %s with %s" % (key, value))
    return value


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
    stampy.stampy.dbsql(sql)
    return


def deleteconfig(word):
    """
    Deletes a config parameter in database
    :param word: key to remove
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "DELETE FROM config WHERE key='%s';" % word
    logger.debug(msg="rmconfig: %s" % word)
    stampy.stampy.dbsql(sql)
    return
