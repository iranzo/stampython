#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing config commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

from prettytable import from_db_cursor

import stampy.stampy
from stampy.i18n import _
from stampy.i18n import _L


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    triggers = ["^/config", "^/gconfig", "^/lconfig"]
    return triggers


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower()[0:7] == "/config":
            configcommands(message)
        elif text.split()[0].lower()[0:8] == "/gconfig":
            configcommands(message)
        elif text.split()[0].lower()[0:8] == "/lconfig":
            configcommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    if stampy.stampy.is_owner(message):
        commandtext = _("Use `/config show` to get a list of defined config settings\n")
        commandtext += _("Use `/config set <key>=<value>` to define a value for key\n")
        commandtext += _("Use `/config delete <key>` to delete key\n\n")
    if stampy.stampy.is_owner_or_admin(message):
        commandtext += _("/gconfig acts on 'effective chat' while /lconfig on 'local chat' (for linked))\n")
        commandtext += _("Use `/[g|l]config show` to get a list of defined group config settings\n")
        commandtext += _("Use `/[g|l]gconfig set <key>=<value>` to define a value for key\n")
        commandtext += _("Use `/[g|l]gconfig delete <key>` to delete key\n\n")
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

    if texto.split(' ')[0] == "/config" and stampy.stampy.is_owner(message):
        gid = 0
    elif texto.split(' ')[0] == "/lconfig":
        gid = chat_id
    else:
        gid = stampy.stampy.geteffectivegid(chat_id)

    # Only users defined as 'owner' or 'admin' can perform commands
    if stampy.stampy.is_owner_or_admin(message):
        logger.debug(msg=_L("Command: %s by %s") % (texto, who_un))
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
                text = showconfig(key=word, gid=gid)
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                break
            if case('delete'):
                key = word
                # Define valid keys for each role
                if gid > 0:  # user private chat
                    validkeys = ['language', 'currency', 'modulo', 'stock',
                                 'espp']
                elif gid < 0:  # group chat or channel
                    validkeys = ['language', 'currency', 'modulo', 'stock',
                                 'espp', 'isolated', 'admin', 'welcome',
                                 'maxage']
                else:
                    validkeys = []

                if key in validkeys or gid == 0:
                    text = _("Deleting config for `%s`") % key
                    deleteconfig(key=key, gid=gid)
                else:
                    text = _("Key *%s* not allowed to be removed") % key
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")

                break

            if case('set'):
                word = " ".join(texto.split(' ')[2:])
                if "=" in word:
                    key = word.split('=')[0]

                    # Define valid keys for each role
                    if gid > 0:  # user private chat
                        validkeys = ['language', 'currency', 'modulo',
                                     'stock', 'espp']
                    elif gid < 0:  # group chat or channel
                        validkeys = ['language', 'currency', 'modulo',
                                     'stock', 'espp', 'isolated', 'admin',
                                     'welcome', 'maxage']
                    else:
                        validkeys = []

                    if key in validkeys or gid == 0:
                        value = word.split('=')[1]
                        setconfig(key=key, value=value, gid=gid)
                        text = _("Setting config for `%s` to `%s`") % (key, value)
                    else:
                        text = _("Key *%s* not allowed to be set") % key
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                break
            if case():
                break

    return


def showconfig(key=False, gid=0):
    """
    Shows configuration in database for a key or all values
    :param gid: group ID to check
    :param key: key to return value for
    :return: Value stored
    """
    logger = logging.getLogger(__name__)
    if key:
        # if word is provided, return the config for that key
        string = (key,)
        sql = "SELECT key,value FROM config WHERE key='%s' AND id='%s';" % (string, gid)
        cur = stampy.stampy.dbsql(sql)
        value = cur.fetchone()

        try:
            # Get value from SQL query
            value = value[1]

        except:
            # Value didn't exist before, return 0 value
            value = 0
        text = _("%s has a value of %s for id %s") % (key, value, gid)

    else:
        sql = "select key,value from config WHERE id='%s' ORDER BY key ASC;" % gid
        cur = stampy.stampy.dbsql(sql)
        text = _("Defined configurations for gid %s:\n") % gid
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg=_L("Returning config %s for key %s for id %s") % (text, key, gid))
    return text


def gconfig(key, default=False, gid=0):
    """
    Wrapper to get configuration given key
    :param gid: group ID to check
    :param key: key to get configuration for
    :param default: value to return for key if not define or False
    :return: value in database for that key
    """

    # Try custom group configuration
    value = config(key=key, default=False, gid=gid)
    if value:
        return value
    else:
        # Try general group configuration
        value = config(key=key, default=False, gid=0)
        if value:
            return value
    return default


def config(key, default=False, gid=0):
    """
    Gets configuration from database for a given key
    :param gid: group ID to check
    :param key: key to get configuration for
    :param default: value to return for key if not define or False
    :return: value in database for that key
    """

    # logger = logging.getLogger(__name__)
    string = (key, gid, )
    sql = "SELECT key,value FROM config WHERE key='%s' AND id='%s';" % string
    cur = stampy.stampy.dbsql(sql)
    value = cur.fetchone()

    try:
        # Get value from SQL query
        value = value[1]

    except:
        # Value didn't exist before, return default or False
        value = default

    return value


def setconfig(key, value, gid=0):
    """
    Sets a config parameter in database
    :param gid: group ID to check
    :param key: key to update
    :param value: value to store
    :return:
    """

    logger = logging.getLogger(__name__)
    if config(key=key, gid=gid):
        deleteconfig(key, gid=gid)
    sql = "INSERT INTO config VALUES('%s','%s', '%s');" % (key, value, gid)
    logger.debug(msg=_L("setconfig: %s=%s for id %s") % (key, value, gid))
    stampy.stampy.dbsql(sql)
    return


def deleteconfig(key, gid=0):
    """
    Deletes a config parameter in database
    :param gid: group ID to check
    :param key: key to remove
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "DELETE FROM config WHERE key='%s' AND id='%s';" % (key, gid)
    logger.debug(msg=_L("rmconfig: %s for id %s") % (key, gid))
    stampy.stampy.dbsql(sql)
    return
