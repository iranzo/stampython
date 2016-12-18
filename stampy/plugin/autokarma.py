#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing autokarma commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

from prettytable import from_db_cursor

import stampy.stampy
import stampy.plugin.config


def init():
    """
    Initializes module
    :return:
    """
    return


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0] == "/autok":
            autokcommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    if stampy.plugin.config.config(key='owner') == stampy.stampy.getmsgdetail(message)["who_un"]:
        commandtext = "Use `/autok <key>=<value>` to autokarma" \
                      " value every time key is in" \
                      " the conversation. " \
                      "Multiple values for same key can be added\n\n"
        commandtext += "Use `/autok delete <key>=<value>` to delete" \
                       " autokarma <value> for <key>\n\n"
        commandtext += "Use `/autok list` to list autokarma " \
                       "<key> <value> pairs\n\n"
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

    logger.debug(msg="Command: %s by %s" % (texto, who_un))

    if who_un == stampy.plugin.config.config('owner'):
        logger.debug(msg="Command: %s by Owner: %s" % (texto, who_un))
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
                text = listautok(word)
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
                    text = "Deleting autokarma pair for `%s - %s`" % (
                           key, value)
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                    deleteautok(key=key, value=value)
                break
            if case():
                word = texto.split(' ')[1]
                if "=" in word:
                    key = word.split('=')[0]
                    value = texto.split('=')[1:][0]
                    text = "Setting autokarma for `%s` triggers `%s++`" % (
                           key, value)
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                    createautok(word=key, value=value)

    return


def getautok(key, value):
    """
    Get autok for a key value pair in case it's defined
    :param key: key to search autok
    :param value: value to search autok
    :return: True if existing or False if not
    """

    logger = logging.getLogger(__name__)
    sql = "SELECT * FROM autokarma WHERE key='%s' and value='%s';" % (
          key, value)
    cur = stampy.stampy.dbsql(sql)
    cur.fetchone()
    logger.debug(msg="getautok: %s - %s" % (key, value))

    try:
        # Get value from SQL query
        svalue = value[1]

    except:
        # Value didn't exist before, return 0
        svalue = False

    # We can define recursive aliases, so this will return the ultimate one
    if svalue:
        return True
    return False


def createautok(word, value):
    """
    Creates an autokarma trigger for a word
    :param word: word to use as base for the autokarma
    :param value: values to set as autokarma
    :return:
    """

    logger = logging.getLogger(__name__)
    if not getautok(word, value):
        logger.error(msg="createautok: autok pair %s - %s already exists" % (
                         word, value))
    else:
        sql = "INSERT INTO autokarma VALUES('%s','%s');" % (word, value)
        logger.debug(msg="createautok: %s=%s" % (word, value))
        stampy.stampy.dbsql(sql)
        return True
    return False


def deleteautok(key, value):
    """
    Deletes a key - value pair from autokarma TABLE
    :param key:  key to delete
    :param value: value to delete
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "DELETE FROM autokarma WHERE key='%s' and value='%s';" % (key, value)
    logger.debug(msg="rmautok: %s=%s" % (key, value))
    stampy.stampy.dbsql(sql)
    return True


def listautok(word=False):
    """
    Lists the autok pairs defined for a word, or all the autok
    :param word: word to return value for or everything
    :return: table with autok stored
    """

    logger = logging.getLogger(__name__)
    wordtext = ""

    if not word:
        sql = "select * from autokarma ORDER BY key ASC;"
    else:
        string = (word,)
        sql = "SELECT * FROM autokarma WHERE key='%s' ORDER by key ASC;" % (
              string)
        wordtext = "for word %s" % word

    cur = stampy.stampy.dbsql(sql)

    try:
        # Get value from SQL query
        text = "Defined autokarma triggers %s:\n" % wordtext
        table = from_db_cursor(cur)
            text = "%s\n```%s```" % (text, table.get_string())

    except:
        # Value didn't exist before
        text = "%s has no trigger autokarma" % word

    logger.debug(msg="Returning autokarma %s for word %s" % (text, word))
    return text
