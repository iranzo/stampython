#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing Chuck Norris requests
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import json
import logging
import requests

import stampy.plugin.config
import stampy.stampy
from stampy.i18n import _
from stampy.i18n import _L
import random


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    triggers = ["^/cn"]
    return triggers


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower() == "/cn":
            cn(message=message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = _("Use `/cn <word>` to get a random Chuck Norris quote based on word\n\n")
    return commandtext


def cn(message):
    """
    Processes cn commands
    :param message: Message with the command
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger.debug(msg=_L("Command: %s by %s" % (texto, who_un)))

    # We might be have been given no command, just stock
    try:
        command = texto.split(' ')[1]
    except:
        command = False

    if not command:
        url = "https://api.chucknorris.io/jokes/random"
    else:
        url = "https://api.chucknorris.io/jokes/search?query=%s" % command

    text = "``` "
    # we might get more than one result
    result = json.loads(requests.get(url).content)
    if 'result' in result:
        if result['total'] != 0:
            try:
                totalelem = len(result['result'])
            except:
                totalelem = 0
            if totalelem > 1:
                elem = random.randint(0, totalelem - 1)
            else:
                elem = 0
            text += result['result'][elem]['value']
        else:
            text += "Chuck Norris didn't said a word about it."
    else:
        text += "Chuck Norris didn't said a word about it."

    text += " ```"
    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                              reply_to_message_id=message_id,
                              disable_web_page_preview=True,
                              parse_mode="Markdown")
