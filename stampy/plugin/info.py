#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing info commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging
import stampy.stampy
import stampy.plugin.config
import stampy.plugin.karma


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    return "/info"


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    msgdetail = stampy.stampy.getmsgdetail(message)
    text = msgdetail["text"]

    if text:
        if text.split()[0].lower() == "/info":
            info(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = "Use `/info` to return information" \
                  " about the current message\n\n"
    return commandtext


def info(message):
    """
    Processes info commands in the messages
    :param message: message to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]

    text = "This is update *%s* " % msgdetail["update_id"]
    text += "with message id *%s*.\n" % msgdetail["message_id"]
    text += "This has been sent on chat *%s*, named *%s* on *%s*\n" %\
            (msgdetail["chat_id"], msgdetail["chat_name"], msgdetail["datefor"])
    text += "This message was sent by user id *%s*, with given name *%s*, " \
            "long name *%s* and username *%s*\n" %\
            (msgdetail["who_id"], msgdetail["who_gn"], msgdetail["who_ln"],
             msgdetail["who_un"])

    logger.debug(msg="Returning %s" % text)

    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                              reply_to_message_id=message_id,
                              disable_web_page_preview=True,
                              parse_mode='markdown')
    return
