#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing Dilbert strip requests
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import datetime
import logging

import dateutil.parser
import requests
from lxml import html
from apscheduler.schedulers.background import BackgroundScheduler

import stampy.stampy
import stampy.plugin.stats
import stampy.plugin.config
from stampy.i18n import translate
_ = translate.ugettext

sched = BackgroundScheduler()
sched.start()


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """

    sched.add_job(dilbert, 'cron', id='dilbert', hour='10',
                  replace_existing=True, misfire_grace_time=120)

    triggers = ["^/dilbert"]
    return triggers


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower() == "/dilbert":
            dilbertcommands(message=message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = _("Use `/dilbert <date>` to get Dilbert's comic strip for date or today\n\n")
    if stampy.stampy.is_owner(message):
        commandtext = _("Use `/dilbert trigger` to force sending actual strip to channel\n\n")
    return commandtext


def dilbertcommands(message):
    """
    Searches for commands related to dilbert
    :param message: message to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger.debug(msg=_("Command: %s by %s") % (texto, who_un))

    # We might be have been given no command, just /dilbert
    try:
        date = texto.split(' ')[1]
    except:
        date = ""

    if stampy.stampy.is_owner(message) and date == "trigger":
        # We've been called to update the strip channel
        return dilbert(chat_id=chat_id, date=None,
                       reply_to_message_id=message_id)

    try:
        # Parse date or if in error, use today
        date = dateutil.parser.parse(date)

        # Force checking if valid date
        day = date.day
        month = date.month
        year = date.year
        date = datetime.datetime(year=year, month=month, day=day)
    except:
        date = datetime.datetime.now()

    return dilbert(chat_id=chat_id, date=date, reply_to_message_id=message_id)


def dilbert(chat_id=-1001066352913, date=None, reply_to_message_id=""):
    """
    Sends Dilbert strip for the date provided
    :param chat_id: chat to send image to
    :param date: date to get the strip from that day
    :param reply_to_message_id: Id of the message to send reply to
    :return:
    """
    # http://dilbert.com/strip/2016-11-22

    logger = logging.getLogger(__name__)

    if not date:
        date = datetime.datetime.now()

    url = "http://dilbert.com/strip/%s-%s-%s" % (date.year, date.month, date.day)

    # Ping chat ID to not have chat removed
    stampy.plugin.stats.pingchat(chat_id)

    logger.debug(msg=_("Dilbert comic found"))

    page = requests.get(url)
    tree = html.fromstring(page.content)
    imgsrc = tree.xpath('//img[@class="img-responsive img-comic"]/@src')[0]
    imgtxt = tree.xpath('//img[@class="img-responsive img-comic"]/@alt')[0] + "\n" + url + " - @dilbertstrip"

    return stampy.stampy.sendimage(chat_id=chat_id, image=imgsrc, text=imgtxt, reply_to_message_id=reply_to_message_id)
