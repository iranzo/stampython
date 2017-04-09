#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for changing languate
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

import stampy.stampy
import stampy.plugin.config

import stampy.i18n
import stampy.i18n
import gettext
import os
import locale

_ = stampy.i18n._


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    return "/lang"


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower() == "/lang":
            langcommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    if stampy.plugin.config.config(key='owner') == stampy.stampy.getmsgdetail(message)["who_un"]:
        commandtext = _("Use `/lang <country code>` to change LANG environment variable\n")
    return commandtext


def langcommands(message):
    """
    Processes language configuration commands in the message
    :param message: message to process
    :return:
    """
    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    who_un = msgdetail["who_un"]

    logger = logging.getLogger(__name__)

    # Only users defined as 'owner' can perform commands
    if who_un == stampy.plugin.config.config('owner'):
        logger.debug(msg=_("Command: %s by %s") % (texto, who_un))
        try:
            language = texto.split(' ')[1]
        except:
            language = "C"

        localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../locale')
        try:
            lang = gettext.translation('stampy', localedir=localedir, languages=[language])
            lang.install(unicode=True)
        except:
            lang=False


        try:
            locale.setlocale(locale.LC_ALL, language)
            logger.debug(msg=_("Changing to %s") % language)
        except:
            locale.setlocale(locale.LC_ALL, "C")
            logger.debug(msg=_("Failed changing to %s") % language)

        logger.debug(msg=_("Changing translator to: %s") % lang)
        localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
        translate = gettext.translation('stampy', localedir, fallback=True)
        stampy.i18n.translate = translate

    return
