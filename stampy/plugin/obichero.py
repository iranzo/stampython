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

sched = BackgroundScheduler()
sched.start()


def init():
    """
    Initializes module
    :return:
    """

    sched.add_job(obichero, 'cron', id='obichero', hour='11',
                  replace_existing=True)

    return


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0] == "/obichero":
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
    return commandtext


def obicherocommands(message):
    """
    Searches for commands related to dilbert
    :param message: message to process
    :return:
    """

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger = logging.getLogger(__name__)
    logger.debug(msg="Command: %s by %s" % (texto, who_un))

    # We might be have been given no command, just /dilbert
    try:
        date = texto.split(' ')[1]
    except:
        date = ""

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


def obichero(chat_id=-1001069507044, date=datetime.datetime.now(),
             reply_to_message_id=""):
    """
    Sends Mel's strip for the date provided
    :param chat_id: chat to send image to
    :param date: date to get the strip from that day
    :param reply_to_message_id: Id of the message to send reply to
    :return:
    """
    url = "http://obichero.blogspot.com/feeds/posts/default"
    feed = feedparser.parse(url)

    tira = []
    for item in reversed(feed["items"]):
        dateitem = dateutil.parser.parse(item["published"][:16])
        if date.year == dateitem.year and date.month == dateitem.month and \
           date.day == dateitem.day:
            tira.append(item)

    for item in tira:
        url = item['link']
        tree = html.fromstring(item['summary'])
        imgsrc = tree.xpath('//img/@src')[0]
        imgtxt = item['title_detail']['value'] + "\n" + url + " - @obicherounofficial"
        stampy.stampy.sendimage(chat_id=chat_id, image=imgsrc, text=imgtxt, reply_to_message_id=reply_to_message_id)
    return
