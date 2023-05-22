#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing uptime commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import datetime
import logging
import time

import dateutil.parser
from babel.dates import format_timedelta

import stampy.plugin.config
import stampy.stampy
from stampy.i18n import _
from stampy.i18n import _L


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """

    # Store initialization time as 'bot start time'
    date = stampy.stampy.utize(datetime.datetime.now())
    stampy.plugin.config.setconfig(key='uptime', gid=0, value=date)
    return ["^/uptime"]


def run(message):    # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    msgdetail = stampy.stampy.getmsgdetail(message)
    if text := msgdetail["text"]:
        if text.split()[0].lower()[:7] == "/uptime":
            uptime(message)
    return


def help(message):    # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    return _(
        "Use `/uptime` to return information about running time of the bot\n\n"
    )


def uptime(message):
    """
    Processes uptime commands in the messages
    :param message: message to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]

    datelast = stampy.stampy.utize(dateutil.parser.parse(stampy.plugin.config.config(key='uptime', gid=0)))
    datelastfor = datelast.strftime('%Y/%m/%d %H:%M:%S')
    datelastts = time.mktime(datelast.timetuple())
    date = stampy.stampy.utize(datetime.datetime.now())
    datefor = date.strftime('%Y/%m/%d %H:%M:%S')
    dateforts = time.mktime(date.timetuple())
    elapsed = dateforts - datelastts

    text = _("Bot was started at: %s\n") % datelastfor
    text += _("Now it is: %s\n") % datefor
    text += _("Elapsed time: %s (seconds)\n") % elapsed
    text += _("Elapsed time: %s \n") % format_timedelta(datetime.timedelta(seconds=elapsed), locale=stampy.stampy.language)

    logger.debug(msg=_L("Returning %s") % text)

    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                              reply_to_message_id=message_id,
                              disable_web_page_preview=True,
                              parse_mode='markdown')
    return
