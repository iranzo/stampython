#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for forwarding messages
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import json
import logging
import urllib
from time import sleep

from prettytable import from_db_cursor

import stampy.plugin.config
import stampy.stampy
from stampy.i18n import _
from stampy.i18n import _L


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    triggers = ["^/forward"]
    return triggers


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)
    text = msgdetail["text"]

    if text:
        if text.split()[0].lower()[0:8] == "/forward":
            logger.debug(msg=_L("Processing forward commands"))
            forwardcommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    if stampy.stampy.is_owner(message):
        commandtext = _("Use `/forward <source>=<target>` to assign a forwarder\n")
        commandtext += _("Use `/forward list` to list forwards defined\n")
        commandtext += _("Use `/forward delete <source>=<target>` to remove a forwarding\n\n")
    return commandtext


def doforward(message, target):
    """
    Forwards a message target chatid
    :param message: Message to process (contaning all details)
    :param target: Target chat_id
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    text = msgdetail['text']

    url = "%s%s/forwardMessage" % (stampy.plugin.config.config(key="url"),
                                   stampy.plugin.config.config(key='token'))

    message = "%s?chat_id=%s&from_chat_id=%s&message_id=%s" % (url, target, chat_id, message_id)

    code = False
    attempt = 0
    exitcode = 0
    while not code:
        result = json.load(urllib.urlopen(message))
        code = result['ok']
        logger.error(msg=_L("ERROR (%s) forwarding message: Code: %s : Text: %s") % (attempt, code, result))
        if code == 'False' or not code:
            if result['error_code'] == 403 and result['description'] == u'Forbidden: bot was blocked by the user':
                # User hasn't initiated or has blocked direct messages from bot
                attempt = 60
                exitcode = 'blocked'

            if result['error_code'] == 400 and result['description'] == u'Bad Request: message to forward not found':
                # Message not found on chat
                attempt = 60
                exitcode = '0'

            if result['error_code'] == 400 and result['description'] == u'Bad Request: chat not found':
                # Message not found on chat
                attempt = 60
                exitcode = '0'

        attempt += 1
        sleep(1)
        # exit after 60 retries with 1 second delay each
        if attempt > 60:
            logger.error(msg=_L("PERM ERROR forwarding message: Code: %s : Text: %s") % (code, result))
            code = True
    logger.debug(msg=_L("forwarding message: Code: %s : Text: %s") % (code, text))
    return exitcode


def forwardmessage(message):
    """
    Forwards a message based on id/chatid to target chatid
    :param message: Message to process (contaning all details)
    :return:
    """

    logger = logging.getLogger(__name__)

    # If forward plugin is enabled, process
    forward = False
    for i in stampy.stampy.plugs:
        try:
            if 'forward' in i.__name__:
                forward = True
        except:
            continue
    if forward:
        msgdetail = stampy.stampy.getmsgdetail(message)
        chat_id = msgdetail["chat_id"]

        for target in getforward(source=chat_id):
            doforward(message=message, target=target)
    else:
        logger.debug(msg=_L("Forward plugin not enabled, skipping"))
    return


def forwardcommands(message):
    """
    Processes forward commands in the message texts
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
    if stampy.stampy.is_owner(message):
        logger.debug(msg=_L("Command: %s by Owner: %s") % (texto, who_un))
        try:
            command = texto.split(' ')[1]
        except:
            command = ""
        try:
            source = texto.split(' ')[2].lower()
        except:
            source = ""

        for case in stampy.stampy.Switch(command):
            if case('list'):
                text = listforward(source)
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                break
            if case('delete'):
                word = texto.split(' ')[2]
                if "=" in word:
                    source = word.split('=')[0]
                    target = texto.split('=')[1:][0]
                    text = _("Deleting forward for `%s -> %s`") % (source, target)
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                    deleteforward(source=source, target=target)
                break
            if case():
                word = command
                if "=" in word:
                    source = word.split('=')[0]
                    target = texto.split('=')[1:][0]
                    text = _("Setting forward for `%s` to `%s`") % (source, target)
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                    createforward(source=source, target=target)
    return


def deleteforward(source, target):
    """
    Deletes a pair from forward database
    :param source: chat_id for source
    :param target: chat_id for target
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "DELETE FROM forward WHERE source='%s' AND target='%s';" % (source, target)
    logger.debug(msg="rmforward: %s -> %s" % (source, target))
    stampy.stampy.dbsql(sql)
    return


def listforward(source=False):
    """
    Lists the forwards defined for a source or all defined
    :param source: chatid
    :return: table with forwards defined
    """

    logger = logging.getLogger(__name__)
    if source:
        # if source is provided, return the forwards for that source
        string = (source,)
        sql = "SELECT source,target FROM forward WHERE source='%s' ORDER by source ASC;" % string
        cur = stampy.stampy.dbsql(sql)
        target = cur.fetchone()

        try:
            # Get value from SQL query
            target = target[1]

        except:
            # Value didn't exist before, return 0 value
            target = ""
        text = _("%s has a forward %s") % (source, target)

    else:
        sql = "SELECT source,target from forward ORDER BY source ASC;"
        cur = stampy.stampy.dbsql(sql)
        text = _("Defined forwards:\n")
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg=text)
    return text


def createforward(source, target):
    """
    Creates a forward for specified source
    :param source: chatid for source messages
    :param target: chatid for destination messages
    :return:
    """

    logger = logging.getLogger(__name__)
    if getforward(source) == target:
        logger.error(msg=_L("createforward: circular reference %s=%s") % (source, target))
    else:
        sql = "INSERT INTO forward VALUES('%s','%s');" % (source, target)
        logger.debug(msg=_L("createforward: %s=%s" % (source, target)))
        stampy.stampy.dbsql(sql)
        return
    return False


def getforward(source):
    """
    Get forwards for source if it's defined
    :param source: chatid to search for
    :return: target if existing or False if not
    """

    logger = logging.getLogger(__name__)
    string = (source,)
    sql = "SELECT target FROM forward WHERE source='%s';" % string
    cur = stampy.stampy.dbsql(sql)
    rows = cur.fetchall()
    for target in rows:
        logger.debug(msg=_L("getforward: %s -> %s" % (source, target)))
        yield target[0]
