#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing help commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

import stampy.plugins
import stampy.stampy
from stampy.i18n import translate
_ = translate.ugettext


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """

    triggers = ["^/help"]
    return triggers


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower() == "/help":
            helpcommands(message=message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = _("Use `/help` to display commands help\n\n")
    commandtext += _("Read about announcements at https://t.me/redkennews\n\n")
    return commandtext


def helpcommands(message):
    """
    Searches for commands related to help
    :param message: nessage to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger.debug(msg=_("Command: %s by %s") % (texto, who_un))

    if chat_id != msgdetail['who_id']:
        # Provide text on public channel
        text = _("Message sent privately, open a chat with @%s and say hi to receive private messages or read https://github.com/iranzo/stampython/blob/master/README.md\n") % stampy.stampy.getme()['username']
        stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                  reply_to_message_id=message_id)

        # We asked for help on public channel, answer privately
        chat_id = msgdetail['who_id']
        message_id = False

    # Call plugins to process help messages
    commandtext = ""

    for i in stampy.stampy.plugs:
        if i.__name__.split(".")[-1] != "help":
            commandtext += i.help(message=message)

    for i in stampy.stampy.plugs:
        if i.__name__.split(".")[-1] == "help":
            commandtext += i.help(message=message)

    logger.debug(msg=_("Command: %s") % texto)

    return stampy.stampy.sendmessage(chat_id=chat_id, text=commandtext,
                                     reply_to_message_id=message_id,
                                     parse_mode="Markdown")
