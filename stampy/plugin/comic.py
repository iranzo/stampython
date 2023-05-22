#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing comic commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import datetime
import logging
from urlparse import urlparse

import dateutil.parser
import feedparser
import requests
from lxml import html
from prettytable import from_db_cursor

import stampy.plugin.alias
import stampy.plugin.config
import stampy.plugin.karma
import stampy.plugin.stats
import stampy.stampy
from stampy.i18n import _
from stampy.i18n import _L


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    botname = stampy.stampy.getme()

    triggers = ["^/comic"]

    if botname == 'redken_bot':
        stampy.stampy.cronme(name="comic", interval=30)

    for comic in getcomics():
        triggers.extend([f"/{comic}"])

    return triggers


def cron():
    """
    Function to be executed periodically
    :return:
    """

    comics()


def run(message):    # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    if text:
        = stampy.stampy.getmsgdetail(message)["text"]:
        comiccommands(message)
    return None


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    commandtext += _("Use `/comic list` to list comics defined\n")
    commandtext += _("Use `/comic all` to show all actual comics\n")
    if stampy.stampy.is_owner(message):
        commandtext += _(
            "Use `/comic trigger` to send comics to chats defined\n\n")
    return commandtext


def comiccommands(message):
    """
    Processes comic commands in the message texts
    :param message: Message to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger.debug(msg=_L("Command: %s by %s") % (texto, who_un))

    if stampy.stampy.is_owner_or_admin(message):
        logger.debug(msg=_L("Command: %s by Owner: %s") % (texto, who_un))
        try:
            command = texto.split(' ')[1]
        except:
            command = False

        for case in stampy.stampy.Switch(command):
            if case('list'):
                text = listcomics()
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                break

            if case('trigger'):
                comics()
                break

            if case('all'):
                comics(name=False, message=message, all=True)
                break

            if case():
                # we might been have called by direct triggers or by comic
                # name, so show only that comic
                trigger = texto.split(' ')[0]
                if "/" in trigger and trigger != "/comic":
                    comics(name=trigger[1:], message=message, all=True)
                else:
                    comics(name=command, message=message, all=True)
                break
    return


def getcomics():
    """
    Get comics
    :return: List of comic triggers
    """

    logger = logging.getLogger(__name__)
    sql = "SELECT distinct name FROM comic;"
    cur = stampy.stampy.dbsql(sql)
    data = cur.fetchall()
    value = [row[0] for row in data]
    logger.debug(msg=_L("getcomics: %s") % value)

    return value


def listcomics():
    """
    Lists the comic strips defined
    :return: table with comics stored
    """

    logger = logging.getLogger(__name__)

    sql = "select name,lastchecked, type,url  from comic ORDER BY name ASC;"
    cur = stampy.stampy.dbsql(sql)

    try:
        # Get value from SQL query
        text = _("Defined comic strips:\n")
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    except:
        text = ""

    logger.debug(msg=_L("Returning comics"))
    return text


def comics(message=False, name=False, all=False):
    """
    Shows Comics for 'name'
    :param message:  Message invoking comic
    :param name: Name of the comic to show
    :param all: Show just new ones or all for today
    """
    logger = logging.getLogger(__name__)

    date = datetime.datetime.now()

    sql = (
        f"SELECT name,type,channelgid,lastchecked,url from comic WHERE name='{name}';"
        if name
        else "SELECT name,type,channelgid,lastchecked,url from comic"
    )
    if message:
        msgdetail = stampy.stampy.getmsgdetail(message)
        message_id = msgdetail["message_id"]
    else:
        msgdetail = False
        message_id = False

    cur = stampy.stampy.dbsql(sql)
    comicsupdated = []
    gidstoping = []
    for row in cur:
        (name, tipo, channelgid, lastchecked, url) = row
        chat_id = msgdetail["chat_id"] if message else channelgid
        if all:
            datelast = datetime.datetime(year=1981, month=1, day=24)
        else:
            try:
                # Parse date or if in error, use today
                datelast = dateutil.parser.parse(lastchecked)

                # Force checking if valid date
                day = datelast.day
                month = datelast.month
                year = datelast.year
                datelast = datetime.datetime(year=year, month=month, day=day)
            except:
                datelast = datetime.datetime(year=1981, month=1, day=24)

        if (date - datelast).days >= 1:
            # Last checked comic was more than 1 day ago
            logger.debug(msg=_L("Comic: %s, last: %s, now: %s, url: %s") % (name, datelast, date, url))

            if tipo == 'rss':
                # Comic is rss feed, process
                comic = comicfromrss(url=url)
            elif tipo == 'url':
                # Comic is URL based
                comic = comicfromurl(name=name)
            elif tipo == 'rssurl':
                # Comic uses RSS feed to link to posts containing images
                # grab URL via RSS

                txt, img, urlpage = comicfromrss(url)

                # Process URL with xpaths
                comic = comicfromurl(name=name, forceurl=urlpage)

            else:
                comic = (False, False, False)

            title = comic[0]
            img = comic[1]
            url = comic[2]

            imgtxt = "%s\n%s - @redken_strips" % (title, url)

            try:
                code = stampy.stampy.sendimage(chat_id=chat_id, image=img, text=imgtxt, reply_to_message_id=message_id)
            except:
                code = False

            if code:
                gidstoping.append(chat_id)
                comicsupdated.append(name)

    # We were invoked in cron job, not updating database of last pushed comic
    #  strips
    if not all:
        datefor = date.strftime('%Y/%m/%d')
        # Update comics with results so they are not shown next time
        for comic in stampy.stampy.getitems(comicsupdated):
            # Update date in SQL so it's not invoked again
            sql = f"UPDATE comic SET lastchecked='{datefor}' where name='{comic}'"
            logger.debug(msg=_L("Updating last checked as per %s") % sql)
            stampy.stampy.dbsql(sql=sql)

        # Update stats for chats where sent comic
        for gid in stampy.stampy.getitems(gidstoping):
            stampy.plugin.stats.pingchat(chatid=gid)


def comicfromrss(url):
    """
    Returns title, img and post url
    :param url: url to process
    :return:
    """

    logger = logging.getLogger(__name__)

    date = datetime.datetime.now()

    feed = feedparser.parse(url)
    tira = []
    for item in reversed(feed["items"]):
        dateitem = dateutil.parser.parse(item["updated"][:16])
        if date.year == dateitem.year and date.month == dateitem.month and date.day == dateitem.day:
            tira.append(item)

    logger.debug(msg=_L("# of Comics for today: %s") % len(tira))

    imgtxt = False
    imgsrc = False
    url = False

    for item in tira:
        url = item['link']
        try:
            tree = html.fromstring(item['summary'])
            imgsrc = tree.xpath('//img/@src')[0]
        except:
            try:
                imgsrc = item['media_content'][0]['url']
            except:
                imgsrc = False
        imgtxt = item['title_detail']['value']

    return imgtxt, imgsrc, url


def comicfromurl(name, forceurl=False):
    """
    Returns title, img and post url
    :param name: name of comic to process
    :return:
    """

    logger = logging.getLogger(__name__)

    sql = f"SELECT url, imgxpath, txtxpath from comic WHERE name='{name}';"
    cur = stampy.stampy.dbsql(sql)

    date = datetime.datetime.now()

    day = date.day
    month = date.month
    year = date.year

    for row in cur:
        (url, imgxpath, txtxpath) = row

    if forceurl:
        # If we pass url via parameters, force use that one
        url = forceurl

    while '#year#' in url or '#month#' in url or '#day#' in url:
        items = ['year', 'month', 'day']
        for item in items:
            if item in url:
                url = url.replace(f'#{item}#', '%02d', 1)
                if item == 'year':
                    url = url % year
                elif item == 'month':
                    url = url % month
                elif item == 'day':
                    url = url % day

    try:
        page = requests.get(url)

    except:
        imgtxt = False
        imgsrc = False
        page = False

    if page and url == page.url:
        tree = html.fromstring(page.content)
        if imgxpath and imgxpath != 'False':
            try:
                imgsrc = tree.xpath(f'{imgxpath}')[0]
            except:
                imgsrc = False
        else:
            imgsrc = url

        if txtxpath and txtxpath != 'False':
            try:
                imgtxt = tree.xpath(f'{txtxpath}')[0]
            except:
                imgtxt = False
        else:
            imgtxt = f"{name}: {year}/{month}/{day}"

        if imgsrc:
            if imgsrc[:2] == "//":
                imgsrc = f'http:{imgsrc}'

            elif imgsrc[0] == "/":
                # imgsrc is relative, prepend url
                parsed_uri = urlparse(url)
                domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                imgsrc = domain + imgsrc
    else:
        imgtxt = False
        imgsrc = False
        url = False

    return imgtxt, imgsrc, url
