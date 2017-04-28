#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing hilight commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

from prettytable import from_db_cursor

import stampy.stampy
import stampy.plugin.config
import stampy.plugin.karma
import stampy.plugin.alias
import stampy.plugin.stats
import stampy.plugin.forward
from stampy.i18n import translate
_ = translate.ugettext


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """

    triggers = ["^/hilight"]
    triggers.extend(stampy.stampy.getitems(gethilightwords(uid=False)))

    return triggers


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    code = None
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower() == "/hilight":
            code = True
            hilightcommands(message)
        hilightwords(message)

    return code


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = _("Use `/hilight add <word>` to add word to your "
                    "hilight list so messages in channels you're member "
                    "will be forwarded privately to you (need to start "
                    "prior conversation with bot)\n\n")
    commandtext += _("Use `/hilight delete <word>` to delete word "
                     "from your hilight list\n\n")
    commandtext += _("Use `/hilight list` to list hilights enabled "
                     "for your user\n\n")
    return commandtext


def hilightcommands(message):
    """
    Processes hilight commands in the message texts
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]
    who_id = msgdetail["who_id"]

    logger.debug(msg=_("Command: %s by user: %s") % (texto, who_un))
    try:
        command = texto.split(' ')[1]
    except:
        command = False
    try:
        word = texto.split(' ')[2]
    except:
        word = ""

    for case in stampy.stampy.Switch(command):
        if case('list'):
            text = listhilight(word=word, uid=who_id)
            stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                      reply_to_message_id=message_id,
                                      disable_web_page_preview=True,
                                      parse_mode="Markdown")
            break
        if case('delete'):
            text = _("Deleting hilight for `%s`") % word
            stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                      reply_to_message_id=message_id,
                                      disable_web_page_preview=True,
                                      parse_mode="Markdown")
            deletehilight(word=word, uid=who_id)
            break

        if case('add'):
            text = _("Adding hilight for `%s`") % word
            stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                      reply_to_message_id=message_id,
                                      disable_web_page_preview=True,
                                      parse_mode="Markdown")
            createhilight(word=word, uid=who_id)
            break

        if case():
            break

    return


def gethilight(uid, word):
    """
    Get hilight for a uid in case it's defined
    :param word: word to hilight
    :param uid: user to get hilights for
    :return: list of values
    """

    logger = logging.getLogger(__name__)
    sql = "SELECT word FROM hilight WHERE gid='%s' AND word='%s';" % (uid, word)
    cur = stampy.stampy.dbsql(sql)
    data = cur.fetchall()
    value = []
    for row in data:
        # Fill valid values
        value.append(row[0])

    logger.debug(msg="gethilight: %s for uid %s" % (value, uid))

    return value


def gethilightwords(uid=False):
    """
    Get autokeywords
    :return: List of autokeywords
    """

    logger = logging.getLogger(__name__)
    if uid is False:
        sql = "SELECT distinct word FROM hilight;"
    else:
        sql = "SELECT distinct word FROM hilight WHERE gid='%s';" % uid
    cur = stampy.stampy.dbsql(sql)
    data = cur.fetchall()
    value = []
    for row in data:
        # Fill valid values
        value.append(row[0])

    logger.debug(msg="gethilightwords: %s for uid %s" % (value, uid))

    return value


def gethilightuids(word=False):
    """
    Get autokeywords
    :return: List of autokeywords
    """

    logger = logging.getLogger(__name__)
    if word is False:
        sql = "SELECT distinct gid FROM hilight;"
    else:
        sql = "SELECT distinct gid FROM hilight WHERE word='%s';" % word
    cur = stampy.stampy.dbsql(sql)
    data = cur.fetchall()
    value = []
    for row in data:
        # Fill valid values
        value.append(row[0])

    logger.debug(msg="gethilightuids: %s for word %s" % (value, word))

    return value




def createhilight(word, uid):
    """
    Creates an hilight trigger for a word
    :param uid: user to set hilight for
    :param word: word to use as base for the autokarma
    :return:
    """

    logger = logging.getLogger(__name__)
    if gethilight(word=word, uid=uid):
        logger.error(msg=_("createhilight: word %s for uid %s already exists") % (word, uid))
    else:
        sql = "INSERT INTO hilight(word, gid) VALUES('%s', '%s');" % (word, uid)
        logger.debug(msg="createhilight: %s for gid %s" % (word, uid))
        stampy.stampy.dbsql(sql)
        return True
    return False


def deletehilight(word, uid):
    """
    Deletes a word - value pair from autokarma TABLE
    :param uid: user id to delete hilight for
    :param word:  word to delete
    :return:
    """

    logger = logging.getLogger(__name__)
    sql = "DELETE FROM hilight WHERE word='%s' AND gid='%s';" % (word, uid)
    logger.debug(msg="deletehilight: %s for uid %s" % (word, uid))
    logger.debug(msg=sql)
    stampy.stampy.dbsql(sql)
    return True


def listhilight(uid, word=False):
    """
    Lists the hilight defined for a gid or all
    :param uid: filter to group id
    :param word: word to return value for or everything
    :return: table with hilight stored
    """

    logger = logging.getLogger(__name__)
    wordtext = ""

    if not word:
        sql = "select word from hilight WHERE gid='%s' ORDER BY word ASC;" % uid
    else:
        string = (word, uid)
        sql = "SELECT word FROM hilight WHERE word='%s' AND gid='%s' ORDER by word ASC;" % string
        wordtext = _("for word %s for uid %s") % (word, uid)

    cur = stampy.stampy.dbsql(sql)

    try:
        # Get value from SQL query
        text = _("Defined hilight triggers %s:\n") % wordtext
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())

    except:
        # Value didn't exist before
        text = _("%s has no trigger hilight") % word

    logger.debug(msg=_("Returning hilight %s for word %s") % (text, word))
    return text


def hilightwords(message):
    """
    Finds hilight words in messages
    :param message: message to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)
    text_to_process = msgdetail["text"].lower()
    chat_name = msgdetail["chat_name"]
    chat_id = msgdetail["chat_id"]

    keywords = gethilightwords(uid=False)
    uids = gethilightuids(word=False)

    try:
        value = stampy.plugin.stats.getstats(type='chat', id=chat_id)
    except:
        value = False

    if value:
        memberid = stampy.stampy.getitems(value[5])
    else:
        memberid = []

    for uid in uids:
        forward = False
        # Only forward if user is member of group
        if int(uid) in memberid:
            logger.debug(msg=_('User %s is member of group %s') % (uid, chat_id))
            for hilight in keywords:
                if hilight in text_to_process:
                    if hilight in gethilightwords(uid=uid):
                        logger.debug(msg=_('Word %s is in text and forwarding for user') % hilight)
                        forward = True
        else:
            logger.debug(msg=_('User %s NOT member of group %s (%s)') % (uid, chat_id, memberid))

        if forward:
            text = _("Message sent to chat: %s") % chat_name
            stampy.stampy.sendmessage(chat_id=uid, text=text)
            stampy.plugin.forward.doforward(message=message, target=uid)

    return
