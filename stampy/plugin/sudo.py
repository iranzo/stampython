#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing sudo commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

import stampy.plugin.config
import stampy.stampy
from stampy.i18n import _
from stampy.i18n import _L


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """

    # Cleanup leftovers from failed execution
    stampy.plugin.config.deleteconfig(key='overridegid', gid='0')
    stampy.plugin.config.deleteconfig(key='sudo', gid='0')

    return ["^/sudo"]


def run(message):    # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    logger = logging.getLogger(__name__)
    logger.debug(msg=_L("Processing plugin: Code: %s") % __file__)
    if text:
        = stampy.stampy.getmsgdetail(message)["text"]:
        if text.split()[0].lower()[:6] == "/sudo":
            sudocommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = ""

    if stampy.stampy.is_owner(message):
        commandtext = _("Use `/sudo gid=<gid>` to assign group to work on\n")
        commandtext += _("Use `/sudo command` to execute command as if chat id were the one defined\n")
    return commandtext


def sudocommands(message):
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
            if case():
                try:
                    word = texto.split(' ')[1]
                except:
                    word = ""

                if "=" in word:
                    key = word.split('=')[0].lower()
                    if key == 'gid':
                        value = texto.split('=')[1:][0].lower()
                        text = _("Setting gid for sudo to `%s`") % value
                        stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                                  reply_to_message_id=message_id,
                                                  disable_web_page_preview=True,
                                                  parse_mode="Markdown")
                        if value == "":
                            stampy.plugin.config.deleteconfig(
                                key='sudo', gid=0)
                        else:
                            stampy.plugin.config.setconfig(
                                key='sudo', value=value, gid=0)
                elif stampy.plugin.config.config(key='sudo'):
                    # "=" was not in first command, so consider a command to use as 'sudo'

                    # It is a new list, with unique message, so we can alter it
                    stampy.plugin.config.setconfig(
                        key='overridegid', gid=0, value=message['message']['chat']['id'])
                    newmessage = dict(message)

                    # Alter chat ID
                    newmessage['message']['chat']['id'] = int(
                        stampy.plugin.config.config(key='sudo'))

                    # Alter message text
                    type = msgdetail["type"]
                    newmessage[type]['text'] = newmessage[type]['text'][6:]

                    # Alter who_id and who_un
                    newmessage[type]['from']['id'] = int(
                        stampy.plugin.config.config(key='sudo'))

                    newmessages = [newmessage]
                    # Process the new mangled message as if it was sent to a telegram chat
                    stampy.stampy.process(messages=newmessages)
                    stampy.plugin.config.deleteconfig(
                        key='overridegid', gid='0')
    return
