#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing stats commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import datetime
import json
import logging
import urllib

from prettytable import from_db_cursor

import stampy.stampy
import stampy.plugin.config
import stampy.plugin.karma

from apscheduler.schedulers.background import BackgroundScheduler
from stampy.i18n import _

sched = BackgroundScheduler()
sched.start()


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    sched.add_job(dochatcleanup, 'interval', minutes=int(stampy.plugin.config.config('cleanup', 24 * 60)), id='dochatcleanup',
                  replace_existing=True, misfire_grace_time=120)
    sched.add_job(dousercleanup, 'interval', minutes=int(stampy.plugin.config.config('cleanup', 24 * 60)), id='dousercleanup',
                  replace_existing=True, misfire_grace_time=120)

    return "*"


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    msgdetail = stampy.stampy.getmsgdetail(message)
    text = msgdetail["text"]

    # Update stats on the message being processed
    if msgdetail["chat_id"] and msgdetail["chat_name"]:
        updatestats(type="chat", id=msgdetail["chat_id"], name=msgdetail["chat_name"],
                    date=msgdetail["datefor"], memberid=msgdetail["who_id"])

    if msgdetail["name"]:
        updatestats(type="user", id=msgdetail["who_id"], name=msgdetail["name"], date=msgdetail["datefor"],
                    memberid=msgdetail["chat_id"])

    if text:
        if text.split()[0].lower() == "/stats":
            statscommands(message)

    if "@all" in text:
        getall(message)

    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = _("Use `@all` to ping all users in a channel as long as they have username defined in Telegram\n\n")
    if stampy.plugin.config.config(key='owner') == stampy.stampy.getmsgdetail(message)["who_un"]:
        commandtext += _("Use `/stats show <user|chat>` to get stats on last usage\n\n")
    return commandtext


def statscommands(message):
    """
    Processes stats commands in the messages
    :param message: message to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    if who_un == stampy.plugin.config.config('owner'):
        logger.debug(msg=_("Owner Stat: %s by %s") % (texto, who_un))
        try:
            command = texto.split(' ')[1]
        except:
            command = False

        try:
            key = texto.split(' ')[2]
        except:
            key = ""

        for case in stampy.stampy.Switch(command):
            if case('show'):
                text = showstats(key)
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                break
            if case('purge'):
                dochatcleanup()

                break
            if case():
                break

    return


def showstats(type=False):
    """
    Shows stats for defined type or all if missing
    :param type: user or chat or empy for combined
    :return: table with the results
    """
    logger = logging.getLogger(__name__)
    if type:
        sql = "select * from stats WHERE type='%s' ORDER BY count DESC LIMIT 10" % type
    else:
        sql = "select * from stats ORDER BY count DESC LIMIT 10"
    cur = stampy.stampy.dbsql(sql)
    table = from_db_cursor(cur)
    text = _("Defined stats:\n")
    text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg=_("Returning stats %s") % text)
    return text


def updatestats(type=False, id=0, name=False, date=False, memberid=None):
    """
    Updates count stats for a given type
    :param type: user or chat
    :param id: ID to update
    :param name: name of the chat of user
    :param date: date of the update
    :param memberid: ID of the origin to add
        chat_id if type='user'
        user_id if type='chat'
    :return:
    """

    logger = logging.getLogger(__name__)

    try:
        value = getstats(type=type, id=id)
        count = value[4] + 1
    except:
        value = False
        count = 0

    if value:
        newmemberid = value[5]
    else:
        newmemberid = []

    # Only add the id if it was not already stored
    if memberid not in newmemberid:
        if memberid is list:
            newmemberid.extend(memberid)
        else:
            newmemberid.append(memberid)

    newmemberid = stampy.stampy.getitems(newmemberid)

    if 'False' in newmemberid:
        newmemberid.remove('False')
    if 'false' in newmemberid:
        newmemberid.remove('false')
    if False in newmemberid:
        newmemberid.remove(False)
    if "" in newmemberid:
        newmemberid.remove("")
    if [] in newmemberid:
        newmemberid.remove([])

    sql = "DELETE from stats where id='%s'" % id
    stampy.stampy.dbsql(sql)

    sql = "INSERT INTO stats VALUES('%s', '%s', '%s', '%s', '%s', '%s');" % (type, id, name, date, count, json.dumps(newmemberid))

    logger.debug(msg=_("values: type:%s, id:%s, name:%s, date:%s, count:%s, memberid: %s") % (type, id, name, date, count, newmemberid))

    if id:
        try:
            stampy.stampy.dbsql(sql)
        except:
            logger.debug(msg=_("ERROR on updatestats"))
    return


def getchatmemberscount(chat_id=False):
    """
    Get number of users in the actual chat_id
    :param chat_id: Channel ID to query for the number of users
    :return: number of members in chat ID.
    """

    logger = logging.getLogger(__name__)
    url = "%s%s/getChatMembersCount?chat_id=%s" % (stampy.plugin.config.config(key='url'),
                                                   stampy.plugin.config.config(key='token'),
                                                   chat_id)
    try:
        result = str(json.load(urllib.urlopen(url))['result'])
    except:
        result = 0

    logger.info(msg=_("Chat id %s users %s") % (chat_id, result))
    return result


def getoutofchat(chat_id=False):
    """
    Use API call to get the bot out of chats
    :param: chat_id: Channel ID to leave
    """

    logger = logging.getLogger(__name__)
    url = "%s%s/leaveChat?chat_id=%s" % (stampy.plugin.config.config(key='url'),
                                         stampy.plugin.config.config(key='token'),
                                         chat_id)
    try:
        result = str(json.load(urllib.urlopen(url))['result'])
    except:
        result = 0

    logger.info(msg=_("Chat id %s left") % chat_id)
    return result


def dochatcleanup(chat_id=False, maxage=int(stampy.plugin.config.config("maxage", default=180))):
    """
    Checks on the stats database the date of the last update in the chat
    :param chat_id: Channel ID to query in database
    :param maxage: defines maximum number of days to allow chats to be inactive
    """

    logger = logging.getLogger(__name__)

    if chat_id:
        sql = "SELECT * FROM stats WHERE type='chat' and id=%s" % chat_id
    else:
        sql = "SELECT * FROM stats WHERE type='chat'"

    chatids = []
    cur = stampy.stampy.dbsql(sql)

    for row in cur:
        chatid = row[1]
        chatids.append(chatid)

    logger.debug(msg=_("Processing chat_ids for cleanup: %s") % chatids)

    for chatid in chatids:
        (type, id, name, date, count, memberid) = getstats(type='chat', id=chatid)
        if date and (date != "False"):
            chatdate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        else:
            chatdate = datetime.datetime.now()

        now = datetime.datetime.now()

        if (now - chatdate).days > maxage:
            logger.debug(msg=_("CHAT ID %s with name %s and %s inactivity days is going to be purged") % (
                chatid, name, (now - chatdate).days))
            # The last update was older than maxage days ago, get out of chat and
            #  remove karma
            texto = _("Due to inactivity of more than %s days, this bot will exit the channel, please re-add in the future if needed") % maxage
            stampy.stampy.sendmessage(chatid, text=texto)

            getoutofchat(chatid)

            # Remove channel stats
            sql = "DELETE from stats where id='%s';" % chatid
            cur = stampy.stampy.dbsql(sql)

            # Remove users membership that had that channel id
            sql = "SELECT * FROM stats WHERE type='user' and memberid LIKE '%%%s%%';" % chatid
            cur = stampy.stampy.dbsql(sql)

            for line in cur:
                (type, id, name, date, count, memberid) = line
                logger.debug(msg=_("LINE for user %s and memberid: %s will be deleted") % (name, memberid))
                memberid.remove(chatid)
                # Update stats entry in database without the removed chat
                updatestats(type=type, id=id, name=name, date=date, memberid=memberid)
    return


def dousercleanup(user_id=False,
                  maxage=int(stampy.plugin.config.config("maxage",
                                                         default=180))):
    """
    Checks on the stats database the date of the last update from the user
    :param user_id: Channel ID to query in database
    :param maxage: defines maximum number of days to allow chats to be inactive
    """

    logger = logging.getLogger(__name__)

    if user_id:
        sql = "SELECT * FROM stats WHERE type='user' and id=%s" % user_id
    else:
        sql = "SELECT * FROM stats WHERE type='user'"

    userids = []
    cur = stampy.stampy.dbsql(sql)

    for row in cur:
        userid = row[1]
        userids.append(userid)

    logger.debug(msg=_("Processing userids for cleanup: %s") % userids)

    for userid in userids:
        (type, id, name, date, count, memberid) = getstats(type='user',
                                                           id=userid)
        if date and (date != "False"):
            chatdate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        else:
            chatdate = datetime.datetime.now()

        now = datetime.datetime.now()

        if (now - chatdate).days > maxage:
            logger.debug(msg=_("USER ID %s with name %s and %s inactivity days is going to be purged") % (
                userid, name, (now - chatdate).days))

            # Remove channel stats
            sql = "DELETE from stats where id='%s';" % userid
            cur = stampy.stampy.dbsql(sql)

            # Remove users membership that had that channel id
            sql = "SELECT * FROM stats WHERE type='chat' and memberid LIKE '%%%s%%';" % userid
            cur = stampy.stampy.dbsql(sql)

            for line in cur:
                (type, id, name, date, count, memberid) = line
                logger.debug(msg=_("LINE for user %s and memberid: %s will be deleted") % (name, memberid))
                memberid.remove(userid)
                # Update stats entry in database without the removed chat
                updatestats(type=type, id=id, name=name, date=date, memberid=memberid)
    return


def getstats(type=False, id=0, name=False, date=False, count=0):
    """
    Gets statistics for specified element
    :param type: chat or user type to query
    :param id: identifier for user or chat
    :param name: full name
    :param date: date
    :param count: number of messages
    :return: (type, id, name, date, count, memberid)
    """

    logger = logging.getLogger(__name__)
    sql = "SELECT * FROM stats WHERE id='%s' AND type='%s';" % (id, type)
    cur = stampy.stampy.dbsql(sql)
    try:
        value = cur.fetchone()
    except:
        value = False

    memberid = []
    if value:
        (type, id, name, date, count, oldmemberid) = value
        try:
            memberid = json.loads(oldmemberid)
        except:
            memberid = []

    if not count:
        count = 0

    logger.debug(msg=_("values: type:%s, id:%s, name:%s, date:%s, count:%s, memberid:%s") % (type, id, name, date, count, memberid))

    # Ensure we return the modified values
    return type, id, name, date, count, memberid


def getall(message):

    logger = logging.getLogger(__name__)
    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    if "@all" in texto:
        logger.debug(msg=_("@All invoked"))
        (type, id, name, date, count, members) = getstats(type='chat', id=chat_id)

        all = []
        for member in members:
            (type, id, name, date, count, memberid) = getstats(type='user', id=member)
            username = None
            if name:
                for each in name.split():
                    if "@" in each:
                        username = each[1:-1]
            if username and username != "@":
                all.append(username)

        if "@all++" in texto:
            text = ""
            newall = []
            for each in all:
                newall.append("%s++" % each)
            text += " ".join(newall)
            msgdetail["text"] = text
            if newall and text:
                stampy.plugin.karma.karmaprocess(msgdetail)
        else:
            text = _("%s wanted to ping you: ") % who_un
            if text and all:
                text += " ".join(all)
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True)
    return


def pingchat(chatid):
    """
    Updates chat modification time
    :param chatid: Chat to update in stats database
    :return:
    """

    logger = logging.getLogger(__name__)
    (type, id, name, date, count, memberid) = getstats(type='chat', id=chatid)
    date = datetime.datetime.now()
    datefor = date.strftime('%Y-%m-%d %H:%M:%S')
    logger.debug(msg=_("Pinging chat %s: %s on %s") % (chatid, name, datefor))
    updatestats(type="chat", id=chatid, name=name,
                date=datefor, memberid=memberid)
    return
