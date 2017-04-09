#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing alias commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

from prettytable import from_db_cursor

import stampy.stampy
import stampy.plugin.karma
import stampy.plugin.config
from stampy.i18n import translate
_ = translate.ugettext


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    return "/alias"


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    logger = logging.getLogger(__name__)
    logger.debug(msg=_("Processing plugin: Code: %s") % __file__)
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower() == "/alias":
            aliascommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = ""

    if stampy.plugin.config.config(key='owner') == stampy.stampy.getmsgdetail(message)["who_un"]:
        commandtext = _("Use `/alias <key>=<value>` to assign an alias for karma\n")
        commandtext += _("Use `/alias list` to list aliases\n")
        commandtext += _("Use `/alias delete <key>` to remove an alias\n\n")
    return commandtext


def aliascommands(message):
    """
    Processes alias commands in the message texts
    :param message: Message to process
    :return:
    """

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger = logging.getLogger(__name__)
    logger.debug(msg=_("Command: %s by %s") % (texto, who_un))
    if who_un == stampy.plugin.config.config('owner'):
        logger.debug(msg=_("Command: %s by Owner: %s") % (texto, who_un))
        try:
            command = texto.split(' ')[1]
        except:
            command = False
        try:
            word = texto.split(' ')[2].lower()
        except:
            word = ""

        for case in stampy.stampy.Switch(command):
            if case('list'):
                text = listalias(word)
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                break
            if case('delete'):
                key = word
                text = _("Deleting alias for `%s`") % key
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                deletealias(word=key)
                break
            if case():
                word = texto.split(' ')[1]
                if "=" in word:
                    key = word.split('=')[0]
                    value = texto.split('=')[1:][0]
                    text = _("Setting alias for `%s` to `%s`") % (key, value)
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                    createalias(word=key, value=value)
    return


def deletealias(word):
    """
    Deletes a word from the alias database
    :param word:  word to delete
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "DELETE FROM alias WHERE key='%s';" % word
    logger.debug(msg="rmalias: %s" % word)
    stampy.stampy.dbsql(sql)
    return


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
        cur = stampy.stampy.dbsql(sql)
        value = cur.fetchone()

        try:
            # Get value from SQL query
            value = value[1]

        except:
            # Value didn't exist before, return 0 value
            value = 0
        text = _("%s has an alias %s") % (word, value)

    else:
        sql = "select * from alias ORDER BY key ASC;"
        cur = stampy.stampy.dbsql(sql)
        text = _("Defined aliases:\n")
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg=_("Returning aliases %s for word %s") % (text, word))
    return text


def createalias(word, value):
    """
    Creates an alias for a word
    :param word: word to use as base for the alias
    :param value: values to set as alias
    :return:
    """

    logger = logging.getLogger(__name__)
    if getalias(value) == word:
        logger.error(msg=_("createalias: circular reference %s=%s") % (word, value))
    else:
        if not getalias(word) or getalias(word) == word:
            # Removing duplicates on karma DB and add
            # the previous values
            old = stampy.plugin.karma.getkarma(word)
            stampy.plugin.karma.updatekarma(word=word, change=-old)
            stampy.plugin.karma.updatekarma(word=value, change=old)

            sql = "INSERT INTO alias VALUES('%s','%s');" % (word, value)
            logger.debug(msg="createalias: %s=%s" % (word, value))
            stampy.stampy.dbsql(sql)
            return
    return False


def getalias(word):
    """
    Get alias for a word in case it's defined
    :param word: word to search alias
    :return: alias if existing or word if not
    """

    logger = logging.getLogger(__name__)
    string = (word,)
    sql = "SELECT * FROM alias WHERE key='%s';" % string
    cur = stampy.stampy.dbsql(sql)
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
