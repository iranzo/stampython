#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing alias commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

from prettytable import from_db_cursor

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
    return ["^/alias"]


def run(message):    # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    logger = logging.getLogger(__name__)
    logger.debug(msg=_L("Processing plugin: Code: %s") % __file__)
    if text := stampy.stampy.getmsgdetail(message)["text"]:
        if text.split()[0].lower()[:6] == "/alias":
            aliascommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = ""

    if stampy.stampy.is_owner_or_admin(message):
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
    logger.debug(msg=_L("Command: %s by %s") % (texto, who_un))
    if stampy.stampy.is_owner_or_admin(message):
        logger.debug(msg=_L("Command: %s by Owner: %s") % (texto, who_un))
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
                text = listalias(word, gid=stampy.stampy.geteffectivegid(gid=chat_id))
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
                deletealias(word=key, gid=stampy.stampy.geteffectivegid(gid=chat_id))
                break
            if case():
                try:
                    word = texto.split(' ')[1]
                except:
                    word = ""

                if "=" in word:
                    key = word.split('=')[0].lower()
                    value = texto.split('=')[1:][0].lower()
                    text = _("Setting alias for `%s` to `%s`") % (key, value)
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                    createalias(word=key, value=value, gid=stampy.stampy.geteffectivegid(gid=chat_id))
    return


def deletealias(word, gid=0):
    """
    Deletes a word from the alias database
    :param gid: group id to work on
    :param word:  word to delete
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = f"DELETE FROM alias WHERE key='{word}' AND gid='{gid}';"
    logger.debug(msg=f"rmalias: {word} for group {gid}")
    stampy.stampy.dbsql(sql)
    return


def listalias(word=False, gid=0):
    """
    Lists the alias defined for a word, or all the aliases
    :param gid: Group ID to work on
    :param word: word to return value for or everything
    :return: table with alias stored
    """

    logger = logging.getLogger(__name__)
    if word:
        # if word is provided, return the alias for that word
        string = (word, gid)
        sql = "SELECT key,value FROM alias WHERE key='%s' AND gid='%s' ORDER by key ASC;" % string
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
        sql = f"select key,value from alias WHERE gid='{gid}' ORDER BY key ASC;"
        cur = stampy.stampy.dbsql(sql)
        text = _("Defined aliases:\n")
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg=_L("Returning aliases %s for word %s for gid %s") % (text, word, gid))
    return text


def createalias(word, value, gid=0):
    """
    Creates an alias for a word
    :param gid: Group ID to create alias on
    :param word: word to use as base for the alias
    :param value: values to set as alias
    :return:
    """

    logger = logging.getLogger(__name__)
    if getalias(value, gid=gid) == word or word.lower() == value.lower():
        logger.error(msg=_L("createalias: circular reference %s=%s for gid %s") % (word, value, gid))
    elif not getalias(word, gid) or getalias(word, gid) == word:
        # Removing duplicates on karma DB and add
        # the previous values
        old = stampy.plugin.karma.getkarma(word=word, gid=gid)
        stampy.plugin.karma.updatekarma(word=word, change=-old, gid=gid)
        stampy.plugin.karma.updatekarma(word=value, change=old, gid=gid)
        sql = f"INSERT INTO alias(key, value, gid) VALUES('{word}','{value}', '{gid}');"
        logger.debug(msg=f"createalias: {word}={value} for gid {gid}")
        stampy.stampy.dbsql(sql)
        return
    return False


def getalias(word, gid=0):
    """
    Get alias for a word in case it's defined
    :param gid: Group ID to get alias from
    :param word: word to search alias
    :return: alias if existing or word if not
    """

    logger = logging.getLogger(__name__)
    string = (word, gid)
    sql = "SELECT key,value FROM alias WHERE key='%s' AND gid='%s';" % string
    cur = stampy.stampy.dbsql(sql)
    value = cur.fetchone()
    logger.debug(msg=f"getalias: {word} for gid {gid}")

    try:
        # Get value from SQL query
        value = value[1]

    except:
        # Value didn't exist before, return 0
        value = False

    # We can define recursive aliases, so this will return the ultimate one
    if value:
        return getalias(word=value, gid=gid)
    return word.lower() if word else False
