#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing kick commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import json
import logging
import urllib

import stampy.plugin.config
import stampy.plugin.stats
import stampy.stampy
from stampy.i18n import _
from stampy.i18n import _L


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    triggers = ["^/kick", "^/kickban", "^/unban"]
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

    if text:
        kickcommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    if stampy.stampy.is_owner_or_admin(message):
        commandtext += _("Use `/kick <username or id>` to kick user from chat\n\n")
        commandtext += _("Use `/kickban <username or id>` to kick user from chat and ban to forbid new entry\n\n")
        commandtext += _("Use `/unban <user ID>`\n\n")
    return commandtext


def kickcommands(message):
    """
    Processes kick,ban, etc commands in the messages
    :param message: message to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]
    user_id = False

    if stampy.stampy.is_owner_or_admin(message):
        logger.debug(msg=_L("Owner kick/ban/unban: %s by %s") % (texto, who_un))
        try:
            command = texto.split(' ')[0]
        except:
            command = False

        try:
            who = texto.split(' ')[1]
        except:
            who = False

        if not who and msgdetail["replyto"].lower():
            who = msgdetail["replyto"].lower()

        # Retrieve users that match provided id or name
        if command == 'unban':
            users = stampy.plugin.stats.idfromuser(idorname=who, chat_id=False)
        else:
            users = stampy.plugin.stats.idfromuser(idorname=who, chat_id=chat_id)

        # Check if we found one or more users
        if len(users) == 1:
            user_id = users[0]['id']
        else:
            text = _("Not unique user found for command, retry")
            stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                      reply_to_message_id=message_id,
                                      disable_web_page_preview=True,
                                      parse_mode="Markdown")
            return False

        if command and user_id:
            for case in stampy.stampy.Switch(command):
                if case('/kick'):
                    result = kick(chat_id=chat_id, user_id=user_id)
                    if result['ok'] == "True":
                        text = _("User %s kicked out of chat %s") % (user_id, chat_id)
                    else:
                        text = _("Error kicking user %s from chat %s: %s") % (user_id, chat_id, result['description'])

                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True, parse_mode="Markdown")
                    break

                if case('/kickban'):
                    result = kick(chat_id=chat_id, user_id=user_id, ban=True)
                    if result['ok'] == "True":
                        text = _("User %s kicked and banned out of chat %s") % (user_id, chat_id)
                    else:
                        text = _("Error kick+ban user %s from chat %s: %s") % (user_id, chat_id, result['description'])
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True, parse_mode="Markdown")

                    break

                if case('/unban'):
                    result = unban(chat_id=chat_id, user_id=user_id)
                    if result['ok'] == "True":
                        text = _("User %s unbanned out of chat %s") % (user_id, chat_id)
                    else:
                        text = _("Error unbanning user %s from chat %s: %s") % (user_id, chat_id, result['description'])
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True, parse_mode="Markdown")
                    break

                if case():
                    break

    return


def kick(chat_id=False, user_id=False, ban=False):
    """
    Use API call to have the bot kick out of chat
    :param chat_id:  chat id to locate user into
    :param user_id:  user id to kick out of chat
    :param ban: ban user from reentering?
    :return:
    """

    logger = logging.getLogger(__name__)
    result = False

    if chat_id and user_id:
        url = "%s%s/kickChatMember?chat_id=%s&user_id=%s" % (stampy.plugin.config.config(key='url'), stampy.plugin.config.config(key='token'), chat_id, user_id)
        try:
            result = json.load(urllib.urlopen(url))
        except:
            result = False

    logger.debug(msg="RESULT: %s" % result)
    if result['ok'] == 'True':
        logger.info(msg=_L("User %s kicked and banned from %s") % (user_id, chat_id))
        if not ban:
            unban(chat_id=chat_id, user_id=user_id)
    else:
        logger.error(msg=_L("Error when kicking user: %s") % result['description'])

    return result


def unban(chat_id=False, user_id=False):
    """
    Use API call to have the bot unban user
    :param chat_id: Channel ID to unban user on
    :param user_id: User ID to unban
    :return:
    """

    logger = logging.getLogger(__name__)
    result = False

    if chat_id and user_id:
        url = "%s%s/unbanChatMember?chat_id=%s&user_id=%s" % (stampy.plugin.config.config(key='url'), stampy.plugin.config.config(key='token'), chat_id, user_id)

    try:
        result = json.load(urllib.urlopen(url))
    except:
        result = False

    logger.debug(msg="RESULT: %s" % result)

    if result['ok'] == 'True':
        logger.info(msg=_L("User %s unbaned from %s") % (user_id, chat_id))

    return result
