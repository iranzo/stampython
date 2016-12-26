#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing autokarma commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

from prettytable import from_db_cursor

import stampy.stampy
import stampy.plugin.config
import stampy.plugin.karma
import stampy.plugin.alias


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
        autokarmawords(message)

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


def getautok(key):
    """
    Get autok for a key value pair in case it's defined
    :param key: key to search autok
    :return: list of values
    """

    logger = logging.getLogger(__name__)
    sql = "SELECT * FROM autokarma WHERE key='%s';" % key
    cur = stampy.stampy.dbsql(sql)
    data = cur.fetchall()
    value = []
    for row in data:
        # Fill valid values
        value.append(row[1])

    logger.debug(msg="getautok: %s - %s" % (key, value))

    return value


def getautokeywords():
    """
    Get autokeywords
    :return: List of autokeywords
    """

    logger = logging.getLogger(__name__)
    sql = "SELECT distinct key FROM autokarma;"
    cur = stampy.stampy.dbsql(sql)
    data = cur.fetchall()
    value = []
    for row in data:
        # Fill valid values
        value.append(row[0])

    logger.debug(msg="getautokeywords: %s" % value)

    return value


def createautok(word, value):
    """
    Creates an autokarma trigger for a word
    :param word: word to use as base for the autokarma
    :param value: values to set as autokarma
    :return:
    """

    logger = logging.getLogger(__name__)
    if value in getautok(word):
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


def autokarmawords(message):
    """
    Finds commands affecting autokarma in messages
    :param message: message to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)
    text_to_process = msgdetail["text"].lower()

    wordadd = []

    keywords = getautokeywords()
    for autok in keywords:
        if autok in text_to_process:
            # If trigger word is there, add the triggered action
            wordadd.append(getautok(autok) + "++")

    if wordadd:
        # Reduce text in message to just the words we encountered to optimize
        msgdetail["text"] = " ".join(wordadd)
        logger.debug(msg="Autokarma words %s encountered for processing" % msgdetail["text"])
        stampy.plugin.karma.karmaprocess(msgdetail)

    return
