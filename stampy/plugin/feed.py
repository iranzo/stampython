#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing rss feeds
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import datetime
import logging
import time

import dateutil.parser
import feedparser
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

    triggers = ["^/feed"]

    if botname == 'redken_bot':
        stampy.stampy.cronme(name="feed", interval=5)

    return triggers


def cron():
    """
    Function to be executed periodically
    :return:
    """

    feeds()


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    code = None
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        rsscommands(message)
    return code


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    commandtext += _("Use `/feed list` to list feeds defined\n")
    commandtext += _("Use `/feed <name>` show items from feed\n")
    commandtext += _("Use `/feed add <name> <url> <interval:min>` to add a new feed (default interval 1440 mins)\n")
    commandtext += _("Use `/feed delete <name>` to remove an existing feed\n")
    if stampy.stampy.is_owner(message):
        commandtext += _(
            "Use `/feed trigger` to send feeds to chats defined\n\n")
    return commandtext


def rsscommands(message):
    """
    Processes feed commands in the message texts
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
                text = listfeeds(gid=chat_id)
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                break

            if case('trigger'):
                if stampy.stampy.is_owner(message):
                    feeds()
                break

            if case('all'):
                feeds(name=False, message=message)
                break

            if case('add'):
                name = texto.split(' ')[2]
                url = texto.split(' ')[3]
                try:
                    interval = texto.split(' ')[4]
                except:
                    interval = 30
                code = feedadd(name=name, url=url, gid=chat_id,
                               interval=interval)
                if code is not False:
                    text = _("Adding new feed `%s`") % name
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                break

            if case('delete'):
                name = texto.split(' ')[2]
                code = feeddel(name=name, gid=chat_id)
                if code is not False:
                    text = _("Removing feed `%s`") % name
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                              reply_to_message_id=message_id,
                                              disable_web_page_preview=True,
                                              parse_mode="Markdown")
                break

            if case():
                # we might been have called by direct triggers or by feed
                # name, so show only that feed
                trigger = texto.split(' ')[0]
                if "/" in trigger and trigger != "/feed":
                    feeds(name=trigger[1:], message=message)
                else:
                    feeds(name=command, message=message)
                break
    return


def getfeeds():
    """
    Get feeds
    :return: List of feed triggers
    """

    logger = logging.getLogger(__name__)
    sql = "SELECT name FROM feeds"
    cur = stampy.stampy.dbsql(sql)
    data = cur.fetchall()
    value = []
    for row in data:
        # Fill valid values
        value.append(row[0])

    logger.debug(msg=_L("getfeeds: %s") % value)

    return value


def listfeeds(gid=False):
    """
    Lists the feeds defined
    :return: table with feeds stored
    """

    logger = logging.getLogger(__name__)

    sql = "select name,lastchecked,url,interval  from feeds"
    if gid:
        sql = "%s%s" % (sql, " WHERE gid=%s" % gid)
    sql = "%s%s" % (sql, " ORDER BY name ASC;")
    cur = stampy.stampy.dbsql(sql)

    try:
        # Get value from SQL query
        text = _("Defined feeds:\n")
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    except:
        text = ""

    logger.debug(msg=_L("Returning feeds"))
    return text


def feeds(message=False, name=False):
    """
    Shows feeds for 'name'
    :param message:  Message invoking feed
    :param name: Name of the feed to show
    """
    logger = logging.getLogger(__name__)

    date = stampy.stampy.utize(datetime.datetime.now())

    if message:
        msgdetail = stampy.stampy.getmsgdetail(message)
        message_id = msgdetail["message_id"]
        gid = msgdetail["chat_id"]
    else:
        msgdetail = False
        message_id = False
        gid = False

    if name:
        sql = "SELECT name,gid,lastchecked,url,interval,lastitem from feeds WHERE name='%s'" % name
        if gid:
            extra = "and gid='%s';" % gid
            sql = "%s %s" % (sql, extra)
    else:
        sql = "SELECT name,gid,lastchecked,url,interval, lastitem from feeds"
        if gid:
            extra = "WHERE gid='%s'" % gid
            sql = "%s %s" % (sql, extra)

    cur = stampy.stampy.dbsql(sql)
    gidstoping = []

    # Formatted date to write back in database
    datefor = date.strftime('%Y/%m/%d %H:%M:%S')

    # Convert to epoch to properly compare
    dateforts = time.mktime(date.timetuple())

    # Clear the feeds updated
    feedsupdated = []

    for row in cur:
        (name, gid, lastchecked, url, interval, lastitem) = row

        if message:
            chat_id = msgdetail["chat_id"]
        else:
            chat_id = gid

        try:
            # Parse date or if in error, use past
            datelast = stampy.stampy.utize(dateutil.parser.parse(lastchecked))

        except:
            datelast = stampy.stampy.utize(datetime.datetime(year=1981, month=1, day=24))

        try:
            # Parse date or if in error, use past
            datelastitem = stampy.stampy.utize(dateutil.parser.parse(lastitem))

        except:
            datelastitem = stampy.stampy.utize(datetime.datetime(year=1981, month=1, day=24))

        # Get time since last check on the feed (epoch)
        datelastts = time.mktime(datelast.timetuple())
        timediff = int((dateforts - datelastts) / 60)

        # Check if interval is defined or set default
        interval = int(interval)

        if interval == 0:
            interval = 1440

        # If more time has passed since last check than the interval for
        # checks, run the check

        if timediff < interval:
            logger.debug(msg=_L("Skipping feed %s because last run was %s mins ago (%s required)") % (name, timediff, interval))
        else:
            # Get the feed
            feed = feedparser.parse(url)
            news = []
            for item in reversed(feed["items"]):
                dateitem = stampy.stampy.utize(dateutil.parser.parse(item["published"]))

                if stampy.stampy.utize(dateitem) > stampy.stampy.utize(datelastitem):
                    news.append(item)

            logger.debug(msg=_L("# of feeds for today: %s") % len(news))

            # Even if we don't have updated items, update the lastchecked
            # date for interval to work properly
            if len(news) == 0:
                dateitem = stampy.stampy.utize(datelastitem)
                dateitemfor = dateitem.strftime('%Y/%m/%d %H:%M:%S')
                feedsupdated.append({'name': name, 'gid': gid, 'dateitem': dateitemfor})

            for item in news:
                try:
                    url = item['link']
                    title = item['title']
                except:
                    url = False
                    title = False

                if url and title:
                    dateitem = stampy.stampy.utize(dateutil.parser.parse(item["published"]))
                    dateitemfor = dateitem.strftime('%Y/%m/%d %H:%M:%S')
                    itemtext = '*%s* *%s* - [%s](%s)' % (name, dateitem, title, url)
                    try:
                        code = stampy.stampy.sendmessage(chat_id=chat_id, text=itemtext, reply_to_message_id=message_id, parse_mode='Markdown')
                    except:
                        code = False

                    if code:
                        gidstoping.append(chat_id)
                        feedsupdated.append({'name': name, 'gid': gid,
                                             'dateitem': dateitemfor})

    # Update feeds with results so they are not shown next time
    for feed in stampy.stampy.getitems(feedsupdated):
        # Update date in SQL so it's not invoked again
        sql = "UPDATE feeds SET lastchecked='%s',lastitem='%s' where name='%s' and gid='%s'" % (datefor, feed['dateitem'], feed['name'], feed['gid'])
        logger.debug(msg=_L("Updating last checked as per %s") % sql)
        stampy.stampy.dbsql(sql=sql)

    # Update stats for chats where sent feed
    for gid in stampy.stampy.getitems(gidstoping):
        stampy.plugin.stats.pingchat(chatid=gid)


def feedadd(name=False, url=False, gid=0, interval=30):
    """
    Adds a quote for a specified username
    :param gid: group id to filter
    :param name: name of feed
    :param url: rss feed url
    :param interval: interval in minutes between checks
    :return: returns feed ID entry in database
    """

    logger = logging.getLogger(__name__)
    if name and url:
        date = datetime.datetime.now()
        lastchecked = date.strftime('%Y/%m/%d %H:%M:%S')
        sql = "INSERT INTO feeds(name, url, gid, lastchecked, interval) VALUES('%s','%s', '%s', '%s', '%s');" % (name, url, gid, lastchecked, interval)
        cur = stampy.stampy.dbsql(sql)
        logger.debug(msg=_L("feedadd: %s on %s for group %s") % (name, url, gid))
        # Retrieve last id
        sql = "select last_insert_rowid();"
        cur = stampy.stampy.dbsql(sql)
        lastrowid = cur.fetchone()[0]
    else:
        lastrowid = False

    return lastrowid


def feeddel(name=False, gid=0):
    """
    Deletes feed from the database
    :param gid: group id to filter
    :param name: Name of gid to remove
    :return:
    """

    logger = logging.getLogger(__name__)
    code = False
    if name:
        sql = "DELETE FROM feeds WHERE name='%s' AND gid='%s';" % (name, gid)
        logger.debug(msg="feeddel: %s, group: %s" % (name, gid))
        stampy.stampy.dbsql(sql)
        code = True
    return code
