#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing welcome to chats
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging
import stampy.plugin.config
import stampy.stampy
from stampy.i18n import translate

_ = translate.ugettext

def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    triggers = ["*"]
    return triggers


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """

    # Send greetings
    if 'new_chat_participant' in message:
        welcomeuser(message=message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    if stampy.stampy.is_owner_or_admin(message):
        commandtext = _("As admin or owner define 'welcome' to the greeting text sent to new chat members\n\n")
    return commandtext


def welcomeuser(message):
    """
    Greets new users in chat
    :param message: Message to process for newcomer events
    :return:
    """
    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message=message)

    greeting = stampy.plugin.config.config(key='message', default=False)

    logger.debug(msg=_('New user in chat, sending greetings: %s') % greeting)

    if greeting:
        stampy.stampy.sendmessage(chat_id=msgdetail["chat_id"], text=greeting,
                                  reply_to_message_id=msgdetail["message_id"],
                                  parse_mode="Markdown")
    return
