#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing stats commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import datetime
import json
import logging
import urllib

from apscheduler.schedulers.background import BackgroundScheduler
from prettytable import from_db_cursor

import stampy.plugin.config
import stampy.plugin.karma
import stampy.stampy
from stampy.i18n import _

from stampy.i18n import _L

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
    triggers = ["@all", "^/stats", "*", "^/getout"]
    return triggers


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """

    logger = logging.getLogger(__name__)

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
        if text.split()[0].lower()[0:6] == "/stats":
            statscommands(message)
        elif text.split()[0].lower()[0:7] == "/getout":
            getoutcommands(message)

    if "@all" in text:
        getall(message)

    leftchat = False
    try:
        if 'left_chat_participant' in message['message']:
            leftchat = True
    except:
        leftchat = False

    if leftchat:
        chat_id = msgdetail["chat_id"]
        try:
            wholeft = message['message']['left_chat_participant']['id']
        except:
            wholeft = False

        if wholeft:
            logger.debug(msg=_L('Someone with id %s left chat %s, cleaning up') % (wholeft, msgdetail["chat_name"]))

            remove_from_memberid(type='chat', id=chat_id, memberid=wholeft)
            remove_from_memberid(type='user', id=wholeft, memberid=chat_id)

        # Check if it was the bot leaving the channel and cleanup
        try:
            leftusername = message['message']['left_chat_participant']['username']
        except:
            leftusername = False

        if leftusername:
            try:
                botname = stampy.stampy.getme()['username']
            except:
                botname = False

            if leftusername == botname:
                # Bot has been removed from chat, full cleanup of chat data
                logger.debug(msg=_L('Bot has left chat %s, cleaning up') % msgdetail["chat_name"])
                dochatcleanup(chat_id=chat_id, maxage=0)
    migrate = False
    try:
        if 'migrate_to_chat_id' in message['message']:
            migrate = True
    except:
        migrate = False

    if migrate:
        # Chat has been migrated to superchat, so we can migrate all configuration
        chat_id = msgdetail['chat_id']
        new_id = message['message']['migrate_to_chat_id']
        migratechats(oldchat=chat_id, newchat=new_id)

    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = _("Use `@all` to ping all users in a channel as long as they have username defined in Telegram\n\n")
    if stampy.stampy.is_owner(message):
        commandtext += _("Use `/stats show <user|chat>` to get stats on last usage\n\n")
        commandtext += _("Use `/getout <chatid|here>` to have bot leave that chat or current one\n\n")
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

    if stampy.stampy.is_owner(message):
        logger.debug(msg=_L("Owner Stat: %s by %s") % (texto, who_un))
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


def getoutcommands(message):
    """
    Processes getout commands in the messages
    :param message: message to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    who_un = msgdetail["who_un"]

    if stampy.stampy.is_owner(message):
        logger.debug(msg=_L("Owner getout: %s by %s") % (texto, who_un))
        try:
            command = texto.split(' ')[1]
        except:
            command = False

        if command == 'here':
            command = chat_id

        if command:
            try:
                getoutofchat(chat_id=command)
            except:
                pass
    return


def showstats(type=False):
    """
    Shows stats for defined type or all if missing
    :param type: user or chat or empy for combined
    :return: table with the results
    """
    logger = logging.getLogger(__name__)
    if type:
        sql = "select type,id,name,date,count from stats WHERE type='%s' ORDER BY count DESC LIMIT 10" % type
    else:
        sql = "select type,id,name,date,count from stats ORDER BY count DESC LIMIT 10"
    cur = stampy.stampy.dbsql(sql)
    table = from_db_cursor(cur)
    text = _("Defined stats:\n")
    text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg=_L("Returning stats %s") % text)
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

    sql = "INSERT INTO stats(type, id, name, date, count, memberid) VALUES('%s', '%s', '%s', '%s', '%s', '%s');" % (type, id, name, date, count, json.dumps(newmemberid))

    logger.debug(msg=_L("values: type:%s, id:%s, name:%s, date:%s, count:%s, memberid: %s") % (type, id, name, date, count, newmemberid))

    if id:
        try:
            stampy.stampy.dbsql(sql)
        except:
            logger.debug(msg=_L("ERROR on updatestats"))
    return


def remove_from_memberid(type=False, id=0, name=False, date=False, memberid=None):
    """
    Remove memberID from memberid
    :param type: user or chat
    :param id: ID to update
    :param name: name of the chat of user
    :param date: date of the update
    :param memberid: ID of the origin to remove
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
    if memberid in newmemberid:
        newmemberid.remove(memberid)

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

    sql = "INSERT INTO stats(type, id, name, date, count, memberid) VALUES('%s', '%s', '%s', '%s', '%s', '%s');" % (type, id, name, date, count, json.dumps(newmemberid))

    logger.debug(msg=_L("values: type:%s, id:%s, name:%s, date:%s, count:%s, memberid: %s") % (type, id, name, date, count, newmemberid))

    if id:
        try:
            stampy.stampy.dbsql(sql)
        except:
            logger.debug(msg=_L("ERROR on remove_from_memberid"))
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

    logger.info(msg=_L("Chat id %s users %s") % (chat_id, result))
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

    logger.info(msg=_L("Chat id %s left") % chat_id)
    return result


def dochatcleanup(chat_id=False, maxage=int(stampy.plugin.config.config("maxage", default=180))):
    """
    Checks on the stats database the date of the last update in the chat
    :param chat_id: Channel ID to query in database
    :param maxage: defines maximum number of days to allow chats to be inactive
    """

    logger = logging.getLogger(__name__)

    if chat_id:
        sql = "SELECT type,id,name,date,count,memberid FROM stats WHERE type='chat' and id=%s" % chat_id
    else:
        sql = "SELECT type,id,name,date,count,memberid FROM stats WHERE type='chat'"

    chatids = []
    cur = stampy.stampy.dbsql(sql)

    for row in cur:
        chatid = row[1]
        chatids.append(chatid)

    logger.debug(msg=_L("Processing chat_ids for cleanup: %s") % chatids)

    for chatid in chatids:
        (type, id, name, date, count, memberid) = getstats(type='chat', id=chatid)
        if date and (date != "False"):
            chatdate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        else:
            chatdate = datetime.datetime.now()

        now = datetime.datetime.now()

        if (now - chatdate).days > maxage:
            logger.debug(msg=_L("CHAT ID %s with name %s with %s inactivity days is going to be purged") % (
                chatid, name, (now - chatdate).days))
            # The last update was older than maxage days ago, get out of chat and
            #  remove karma
            texto = _("Due to inactivity of more than %s days, this bot will exit the channel, please re-add in the future if needed") % maxage
            stampy.stampy.sendmessage(chatid, text=texto)

            getoutofchat(chatid)

            # Check if this channel was master to another, if so, elect new
            # master, and update karma, autokarma, alias, quote to the new
            # master

            newmaster = 0
            maxmembers = 0

            sql = "SELECT id from config WHERE key='link' and value='%s'" % chatid
            cur = stampy.stampy.dbsql(sql)

            for row in cur.fetchall():
                id = row[0]
                value = getstats(type='chat', id=id)
                if value:
                    newmemberid = value[5]
                else:
                    newmemberid = []

                if len(newmemberid) > maxmembers:
                    maxmembers = len(newmemberid)
                    newmaster = id

            if newmaster != 0:
                logger.debug(msg=_L("The removed channel (%s) was master for others, electing new master: %s") % (chatid, newmaster))
                # Update slaves to new master
                sql = "UPDATE config SET value='%s' WHERE key='link' and value='%s'" % (newmaster, chatid)
                cur = stampy.stampy.dbsql(sql)

                migratechats(oldchat=chat_id, newchat=newmaster, includeall=False)

                # Remove 'link' from the new master so it becomes a master
                stampy.plugin.config.deleteconfig(key='link', gid=newmaster)

            # Two different names because of historical reasons
            for table in ['config', 'stats']:
                # Remove channel stats
                sql = "DELETE from %s where id='%s';" % (table, chatid)
                cur = stampy.stampy.dbsql(sql)

            for table in ['karma', 'quote', 'autokarma', 'alias']:
                # Remove channel stats
                sql = "DELETE from %s where gid='%s';" % (table, chatid)
                cur = stampy.stampy.dbsql(sql)

            # Remove users membership that had that channel id
            string = "%" + "%s" % chatid + "%"
            sql = "SELECT type,id,name,date,count,memberid FROM stats WHERE type='user' and memberid LIKE '%s';" % string
            cur = stampy.stampy.dbsql(sql)

            for line in cur:
                (type, id, name, date, count, memberid) = line
                logger.debug(msg=_L("LINE for user %s and memberid: %s will be deleted") % (name, memberid))
                memberid.remove(chatid)
                # Update stats entry in database without the removed chat
                updatestats(type=type, id=id, name=name, date=date, memberid=memberid)
    return


def migratechats(oldchat, newchat, includeall=True):
    """
    Updates chat references
    :param includeall: defines if stats and config should we moved (chat->supergroup)
    :param oldchat: Old chat id
    :param newchat: Newer chat id
    :return:
    """
    logger = logging.getLogger(__name__)

    # move data from old master to new one (except stats and config)
    logger.debug(msg=_L("Migrating chat id: %s to %s") % (oldchat, newchat))
    for table in ['karma', 'quote', 'autokarma', 'alias']:
        sql = "UPDATE %s SET gid='%s' where gid='%s';" % (table, newchat, oldchat)
        stampy.stampy.dbsql(sql)

    if includeall:
        for table in ['config', 'stats']:
            sql = "UPDATE %s SET id='%s' where id='%s';" % (table, newchat, oldchat)
            stampy.stampy.dbsql(sql)

        # Migrate forward data
        sql = "UPDATE forward SET source='%s' where source='%s;" % (newchat, oldchat)
        stampy.stampy.dbsql(sql)
        sql = "UPDATE forward SET target='%s' where target='%s;" % (newchat, oldchat)
        stampy.stampy.dbsql(sql)
    else:
        # Delete forwards not migrated
        sql = "DELETE FROM forward WHERE source='%s';" % oldchat
        stampy.stampy.dbsql(sql)
        sql = "DELETE FROM forward WHERE target='%s';" % oldchat
        stampy.stampy.dbsql(sql)
    return


def dousercleanup(user_id=False, maxage=int(stampy.plugin.config.config("maxage", default=180))):
    """
    Checks on the stats database the date of the last update from the user
    :param user_id: Channel ID to query in database
    :param maxage: defines maximum number of days to allow chats to be inactive
    """

    logger = logging.getLogger(__name__)

    if user_id:
        sql = "SELECT type,id,name,date,count,memberid FROM stats WHERE type='user' and id=%s" % user_id
    else:
        sql = "SELECT type,id,name,date,count,memberid FROM stats WHERE type='user'"

    userids = []
    cur = stampy.stampy.dbsql(sql)

    for row in cur:
        userid = row[1]
        userids.append(userid)

    logger.debug(msg=_L("Processing userids for cleanup: %s") % userids)

    for userid in userids:
        (type, id, name, date, count, memberid) = getstats(type='user',
                                                           id=userid)
        if date and (date != "False"):
            chatdate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        else:
            chatdate = datetime.datetime.now()

        now = datetime.datetime.now()

        if (now - chatdate).days > maxage:
            logger.debug(msg=_L("USER ID %s with name %s with %s inactivity days is going to be purged") % (
                userid, name, (now - chatdate).days))

            # Remove channel stats
            sql = "DELETE from stats where id='%s';" % userid
            cur = stampy.stampy.dbsql(sql)

            # Remove hilights
            sql = "DELETE from hilight where gid='%s';" % userid
            cur = stampy.stampy.dbsql(sql)

            # Remove users membership that had that channel id
            sql = "SELECT type,id,name,date,count,memberid FROM stats WHERE type='chat' and memberid LIKE '%%%s%%';" % userid
            cur = stampy.stampy.dbsql(sql)

            for line in cur:
                (type, id, name, date, count, memberid) = line
                logger.debug(msg=_L("LINE for user %s and memberid: %s will be deleted") % (name, memberid))
                memberid.remove(userid)
                # Update stats entry in database without the removed chat
                updatestats(type=type, id=id, name=name, date=date, memberid=memberid)

            # Check if user was admin for any channel, and remove
            username = None
            if name:
                for each in name.split():
                    if "@" in each:
                        username = each[1:-1]
            if username and username != "@":
                # userid to remove has username, check admins on config and remove
                string = "%" + username + "%"
                sql = "SELECT id, value FROM config WHERE value like %s" % string

                cur = stampy.stampy.dbsql(sql)

                for row in cur:
                    id = row[0]
                    admins = row[1].split(" ")
                    try:
                        admins.remove(username)
                    except:
                        pass
                    newadmin = " ".join(admins)

                    if len(newadmin) != 0:
                        stampy.plugin.config.setconfig(key='admin',
                                                       value=newadmin, gid=id)
                    else:
                        stampy.plugin.config.deleteconfig(key='admin', gid=id)

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
    sql = "SELECT type,id,name,date,count,memberid FROM stats WHERE id='%s' AND type='%s';" % (id, type)
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

    logger.debug(msg=_L("values: type:%s, id:%s, name:%s, date:%s, count:%s, memberid:%s") % (type, id, name, date, count, memberid))

    # Ensure we return the modified values
    return type, id, name, date, count, memberid


def getall(message):
    """
    Processes 'all' in messages
    :param message:  message to analyze
    :return:
    """
    logger = logging.getLogger(__name__)
    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    if "@all" in texto:
        logger.debug(msg=_L("@All invoked"))
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
    logger.debug(msg=_L("Pinging chat %s: %s on %s") % (chatid, name, datefor))
    updatestats(type="chat", id=chatid, name=name,
                date=datefor, memberid=memberid)
    return
