#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing O Bichero's strip requests
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import datetime
import logging
import dateutil.parser
import feedparser
from apscheduler.schedulers.background import BackgroundScheduler
from lxml import html

import stampy.stampy
import stampy.plugin.stats
import stampy.plugin.config

sched = BackgroundScheduler()
sched.start()


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """

    sched.add_job(obichero, 'cron', id='obichero', hour='15',
                  replace_existing=True, misfire_grace_time=120)

    return "/obichero"


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower() == "/obichero":
            obicherocommands(message=message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = "Use `/obichero <date>` to get O bichero's comic "
    commandtext += "strip for date or today (must be on RSS feed)\n\n"
    if stampy.plugin.config.config(key='owner') == stampy.stampy.getmsgdetail(message)["who_un"]:
        commandtext = "Use `/obichero trigger` to force sending actual " \
                      "strip to channel\n\n"
    return commandtext


def obicherocommands(message):
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

    logger.debug(msg="Command: %s by %s" % (texto, who_un))

    # We might be have been given no command, just /dilbert
    try:
        date = texto.split(' ')[1]
    except:
        date = ""

    if stampy.plugin.config.config(key='owner') == stampy.stampy.getmsgdetail(message)["who_un"] and date == "trigger":
        # We've been called to update the strip channel
        return obichero(chat_id=chat_id, date=date,
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

    return obichero(chat_id=chat_id, date=date, reply_to_message_id=message_id)


def obichero(chat_id=-1001069507044, date=None, reply_to_message_id=""):
    """
    Sends Mel's strip for the date provided
    :param chat_id: chat to send image to
    :param date: date to get the strip from that day
    :param reply_to_message_id: Id of the message to send reply to
    :return:
    """
    url = "http://obichero.blogspot.com/feeds/posts/default"

    logger = logging.getLogger(__name__)

    # Website seems to be pushed in some strange way that makes
    # old posts to be announced as new, causing old strips to be retrieved

    # Ping chat ID to not have chat removed
    stampy.plugin.stats.pingchat(chat_id)

    if not date:
        date = datetime.datetime.now()

    feed = feedparser.parse(url)
    tira = []
    for item in reversed(feed["items"]):
        dateitem = dateutil.parser.parse(item["published"][:16])
        if date.year == dateitem.year and date.month == dateitem.month and date.day == dateitem.day:
            tira.append(item)

    logger.debug(msg="# of Comics for today: %s" % len(tira))

    if tira:
        item = tira[-1]
        url = item['link']
        tree = html.fromstring(item['summary'])
        imgsrc = tree.xpath('//img/@src')[0]
        imgtxt = item['title_detail']['value'] + "\n" + url + " - @obicherounofficial"
        stampy.stampy.sendimage(chat_id=chat_id, image=imgsrc, text=imgtxt, reply_to_message_id=reply_to_message_id)
    return
