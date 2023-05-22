#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing base commands (older telegramcommands)
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
    return ["^/quit"]


def run(message):    # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text and stampy.stampy.is_owner_or_admin(message):
        if text.split()[0].lower()[:6] == "/quit":
            basecommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    if stampy.stampy.is_owner(message):
        commandtext += _("Use `/quit` to exit bot execution\n")
    return commandtext


def basecommands(message):
    """
    Processes link commands in the message
    :param message: message to process
    :return:
    """
    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    who_un = msgdetail["who_un"]

    logger = logging.getLogger(__name__)

    # Only users defined as 'owner' or 'admin' can perform commands
    if stampy.stampy.is_owner(message):
        logger.debug(msg=_L("Command: %s by %s") % (texto, who_un))
        try:
            command = texto.split(' ')[0]
        except:
            command = False

        for case in stampy.stampy.Switch(command):
            if case('/quit'):
                stampy.plugin.config.setconfig('daemon', False)
                break
            if case():
                break
    return
