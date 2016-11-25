#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing help commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

import stampy.plugins
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
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0] == "/help":
            helpcommands(message=message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = "Use `/help` to display commands help\n\n"
    return commandtext


def helpcommands(message):
    """
    Searches for commands related to help
    :param message: nessage to process
    :return:
    """

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger = logging.getLogger(__name__)
    logger.debug(msg="Command: %s by %s" % (texto, who_un))

    # TODO(iranzo) process code
    # Call plugins to process help messages
    commandtext = ""
    for i in stampy.plugins.getPlugins():
        plugin = stampy.plugins.loadPlugin(i)
        commandtext += plugin.help(message=message)

    logger.debug(msg="Command: %s" % texto)

    return stampy.stampy.sendmessage(chat_id=chat_id, text=commandtext,
                                     reply_to_message_id=message_id,
                                     parse_mode="Markdown")
