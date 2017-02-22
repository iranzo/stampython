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

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)
    text = msgdetail["text"]

    if text:
        if text.split()[0].lower() == "/forward":
            forwardcommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    if stampy.plugin.config.config(key='owner') == stampy.stampy.getmsgdetail(message)["who_un"]:
        commandtext = "Use `/forward <source>=<target>`" \
                      " to assign a forwarder\n"
        commandtext += "Use `/forward list` to list forwards defined\n"
        commandtext += "Use `/forward delete <source>=<target>` " \
                       "to remove a forwarding\n\n"
    return commandtext


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
        message_id = msgdetail["message_id"]

        url = "%s%s/forwardMessage" % (stampy.plugin.config.config(key="url"),
                                       stampy.plugin.config.config(key='token'))

        for target in getforward(source=chat_id):
            message = "%s?chat_id=%s&from_chat_id=%s&message_id=%s" % (
                url, target, chat_id, message_id)

            code = False
            attempt = 0
            while not code:
                result = json.load(urllib.urlopen(message))
                code = result['ok']
                logger.error(msg="ERROR (%s) forwarding message: Code: %s : Text: %s" % (
                    attempt, code, result))
                attempt += 1
                sleep(1)
                # exit after 60 retries with 1 second delay each
                if attempt > 60:
                    logger.error(msg="PERM ERROR forwarding message: Code: %s : Text: "
                                     "%s" % (code, result))
                    code = True
            logger.debug(msg="forwarding message: Code: %s : Text: %s" % (code, message))
    else:
        logger.debug(msg="Forward plugin not enabled, skipping")
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
    logger.debug(msg="Command: %s by %s" % (texto, who_un))
    if who_un == stampy.plugin.config.config('owner'):
        logger.debug(msg="Command: %s by Owner: %s" % (texto, who_un))
        try:
            command = texto.split(' ')[1]
        except:
            command = False
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
                    text = "Deleting forward for `%s -> %s`" % (source, target)
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                    deleteforward(source=source, target=target)
                break
            if case():
                word = texto.split(' ')[1]
                if "=" in word:
                    source = word.split('=')[0]
                    target = texto.split('=')[1:][0]
                    text = "Setting forward for `%s` to `%s`" % (source, target)
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
        sql = "SELECT * FROM forward WHERE source='%s' ORDER by source ASC;" % string
        cur = stampy.stampy.dbsql(sql)
        target = cur.fetchone()

        try:
            # Get value from SQL query
            target = target[1]

        except:
            # Value didn't exist before, return 0 value
            target = ""
        text = "%s has a forward %s" % (source, target)

    else:
        sql = "select * from forward ORDER BY source ASC;"
        cur = stampy.stampy.dbsql(sql)
        text = "Defined forwards:\n"
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
        logger.error(msg="createforward: circular reference %s=%s" % (
                         source, target))
    else:
        sql = "INSERT INTO forward VALUES('%s','%s');" % (source, target)
        logger.debug(msg="createforward: %s=%s" % (source, target))
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
        logger.debug(msg="getforward: %s -> %s" % (source, target))
        yield target[0]
