#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing irc-like commands
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
    triggers = ["^/kick", "^/kickban", "^/unban", "^/op", "^/deop",
                "^/topic", "^/mute", "^/unmute", "^/opall", "^/deopall",
                "^/whois"]
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
        irccommands(message)
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
        commandtext += _("Use `/unban <user ID>` to unban user\n\n")
        commandtext += _("Use `/op <user ID>` to grant all privileges\n\n")
        commandtext += _("Use `/deop <user ID>` to remove all privileges\n\n")
        commandtext += _("Use `/opall` to grant op to all\n\n")
        commandtext += _("Use `/deopall` to remove all ops\n\n")
        commandtext += _("Use `/topic <topic>` to change title\n\n")
        commandtext += _("Use `/mute <user ID>` to forbid sending messages\n\n")
        commandtext += _("Use `/unmute <user ID>` to allow sending messages\n\n")
    return commandtext


def irccommands(message):
    """
    Processes kick, ban, etc commands in the messages
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

    try:
        command = texto.split(' ')[0]
    except:
        command = False

    if stampy.stampy.is_owner_or_admin(message):
        logger.debug(msg=_L("Owner kick/ban/unban: %s by %s") % (texto, who_un))

        if command == '/topic':
            newtitle = " ".join(texto.split(' ')[1:])
            dictionary = {
                "'": "",
                "\n": " ",
                u"—": "--"
            }
            newtitle = stampy.stampy.replace_all(text=newtitle,
                                                 dictionary=dictionary)
            topic(chat_id=chat_id, title=newtitle)
            return

        if command == '/opall':
            opall(chat_id=chat_id, extra="op")
            return

        if command == '/deopall':
            opall(chat_id=chat_id, extra="deop")
            return

        try:
            who = texto.split(' ')[1]
        except:
            who = False

        if not who and msgdetail["replyto"]:
            who = msgdetail["replyto"].lower()

        # Retrieve users that match provided id or name
        if command == '/unban':
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
                if case('/opall'):
                    result = opall(chat_id=chat_id, extra="op")
                    if result['ok'] is True or result['ok'] == 'True':
                        text = _("Users opped on chat %s") % chat_id
                    else:
                        text = _("Error opping users from chat %s: %s") % (chat_id, result)

                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True, parse_mode="Markdown")
                    break

                if case('/deopall'):
                    result = opall(chat_id=chat_id, extra="deop")
                    if result['ok'] is True or result['ok'] == 'True':
                        text = _("Users %s deoped on chat %s") % (user_id, chat_id)
                    else:
                        text = _("Error deoping users from chat %s: %s") % (chat_id, result)

                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True, parse_mode="Markdown")
                    break

                if case('/kick'):
                    result = kick(chat_id=chat_id, user_id=user_id)
                    if result['ok'] is True or result['ok'] == 'True':
                        text = _("User %s kicked out of chat %s") % (user_id, chat_id)
                    else:
                        text = _("Error kicking user %s from chat %s: %s") % (user_id, chat_id, result)

                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True, parse_mode="Markdown")
                    break

                if case('/kickban'):
                    result = kick(chat_id=chat_id, user_id=user_id, ban=True)
                    if result['ok'] is True or result['ok'] == 'True':
                        text = _("User %s kicked and banned out of chat %s") % (user_id, chat_id)
                    else:
                        text = _("Error kick+ban user %s from chat %s: %s") % (user_id, chat_id, result['description'])
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True, parse_mode="Markdown")

                    break

                if case('/unban'):
                    result = unban(chat_id=chat_id, user_id=user_id)
                    if result['ok'] is True or result['ok'] == 'True':
                        text = _("User %s unbanned out of chat %s") % (user_id, chat_id)
                    else:
                        text = _("Error unbanning user %s from chat %s: %s") % (user_id, chat_id, result['description'])
                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True, parse_mode="Markdown")
                    break

                if case('/op'):
                    result = op(chat_id=chat_id, user_id=user_id, extra='op')
                    if result['ok'] is True or result['ok'] == 'True':
                        text = _("User %s oped on chat %s") % (user_id, chat_id)
                    else:
                        text = _("Error oping user %s from chat %s: %s") % (user_id, chat_id, result)

                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True, parse_mode="Markdown")
                    break

                if case('/deop'):
                    result = op(chat_id=chat_id, user_id=user_id, extra='deop')
                    if result['ok'] is True or result['ok'] == 'True':
                        text = _("User %s deoped on chat %s") % (user_id, chat_id)
                    else:
                        text = _("Error deoping %s from chat %s: %s") % (user_id, chat_id, result)

                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True, parse_mode="Markdown")
                    break

                if case('/mute'):
                    result = mute(chat_id=chat_id, user_id=user_id,
                                  extra='mute')
                    if result['ok'] is True or result['ok'] == 'True':
                        text = _("User %s muted on chat %s") % (user_id,
                                                                chat_id)
                    else:
                        text = _("Error muting user %s from chat %s: %s") % (
                            user_id, chat_id, result)

                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True, parse_mode="Markdown")
                    break

                if case('/unmute'):
                    result = mute(chat_id=chat_id, user_id=user_id,
                                  extra='unmute')
                    if result['ok'] is True or result['ok'] == 'True':
                        text = _("User %s unmuted on chat %s") % (user_id, chat_id)
                    else:
                        text = _("Error unmuting %s from chat %s: %s") % (
                            user_id, chat_id, result)

                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True, parse_mode="Markdown")
                    break

                if case('/whois'):
                    result = whois(chat_id=chat_id, user_id=user_id)
                    if result['ok'] is True or result['ok'] == 'True':
                        text = _("User %s information: %s") % (user_id, result['result'])
                    else:
                        text = _("Error querying user %s information: %s") % (user_id, result)

                    stampy.stampy.sendmessage(chat_id=chat_id, text=text, reply_to_message_id=message_id, disable_web_page_preview=True)
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
    result = {'ok': False}

    if chat_id and user_id:
        url = "%s%s/kickChatMember?chat_id=%s&user_id=%s" % (stampy.plugin.config.config(key='url'), stampy.plugin.config.config(key='token'), chat_id, user_id)
        try:
            result = json.load(urllib.urlopen(url))
        except:
            result = {'ok': False}
    else:
        result = {'ok': False}

    if result['ok'] is True or result['ok'] == 'True':
        logger.info(msg=_L("User %s kicked and banned from %s") % (user_id, chat_id))
        if not ban:
            unban(chat_id=chat_id, user_id=user_id)
    else:
        logger.error(msg=_L("Error when kicking user: %s") % result)

    return result


def unban(chat_id=False, user_id=False):
    """
    Use API call to have the bot unban user
    :param chat_id: Channel ID to unban user on
    :param user_id: User ID to unban
    :return:
    """

    logger = logging.getLogger(__name__)
    result = {'ok': False}

    if chat_id and user_id:
        url = "%s%s/unbanChatMember?chat_id=%s&user_id=%s" % (stampy.plugin.config.config(key='url'), stampy.plugin.config.config(key='token'), chat_id, user_id)

        try:
            result = json.load(urllib.urlopen(url))
        except:
            result = {'ok': False}

        logger.debug(msg="RESULT: %s" % result)

    if result['ok'] is True or result['ok'] == 'True':
        logger.info(msg=_L("User %s unbaned from %s") % (user_id, chat_id))

    return result


def op(chat_id=False, user_id=False, extra=""):
    """
    Use API call to have the bot op user in
    :param chat_id:  chat id to locate user into
    :param user_id:  user id to op
    :param extra: permissions to set or 'op'|'deop' for full
    :return:
    """

    logger = logging.getLogger(__name__)
    result = {'ok': False}

    # Permissions as defined on API
    permissions_base = ["can_change_info", "can_invite_users", "can_restrict_members", "can_promote_members"]
    permissions_group = permissions_base[:]
    permissions_group.extend(["can_delete_messages"])
    permissions_channel = permissions_base[:]
    permissions_channel.extend(["can_post_messages", "can_edit_messages", "can_delete_messages"])
    permissions_supergroup = permissions_base[:]
    permissions_supergroup.extend(["can_delete_messages", "can_pin_messages"])

    type, id, name, date, count, memberid = stampy.plugin.stats.getstats(id=chat_id)

    if not type:
        # Use API call for getting chat type if not in database
        url = "%s%s/getChat?chat_id=%s" % (stampy.plugin.config.config(key='url'), stampy.plugin.config.config(key='token'), chat_id)
        try:
            result = json.load(urllib.urlopen(url))['result']['type']

        except:
            result = {'ok': False}
    else:
        result = type

    logger.debug(msg=_L('chat type: %s') % result)

    for case in stampy.stampy.Switch(result):
        if case('supergroup'):
            permissions = permissions_supergroup
            break
        if case('channel'):
            permissions = permissions_channel
            break
        if case('group'):
            permissions = permissions_group
            break

        if case('private'):
            permissions = []
            break

        if case():
            break

    # Enable all permissions for OP operations
    if extra == "" or extra == "op":
        value = True
    elif extra == "deop":
        value = False
    if chat_id and user_id:
        for item in permissions:
            extra = "%s&%s=%s" % (extra, item, value)
        url = "%s%s/promoteChatMember?chat_id=%s&user_id=%s&%s" % (stampy.plugin.config.config(key='url'), stampy.plugin.config.config(key='token'), chat_id, user_id, extra)

        try:
            result = json.load(urllib.urlopen(url))
        except:
            result = {'ok': False}

        if result['ok'] is True or result['ok'] == 'True':
            logger.info(msg=_L("User %s has updated permissions: %s on  %s") % (user_id, permissions, chat_id))
        else:
            logger.error(msg=_L("Error when modifying user permission %s: %s") % (permissions, result))

    else:
        result = {'ok': False}

    return result


def topic(chat_id=False, title=False):
    """
    Use API call to have the bot change topic
    :param chat_id:  chat id to locate user into
    :param title: new title to set
    :return:
    """

    logger = logging.getLogger(__name__)
    result = {'ok': False}

    if chat_id and title:
        logger.debug(msg=_L('Setting new title to %s') % title)
        url = "%s%s/setChatTitle?chat_id=%s&title=%s" % (stampy.plugin.config.config(key='url'), stampy.plugin.config.config(key='token'), chat_id, urllib.quote_plus(title.encode('utf-8')))

        try:
            result = json.load(urllib.urlopen(url))
        except:
            result = {'ok': False}
    else:
        result = {'ok': False}

    if result['ok'] is True or result['ok'] == 'True':
        logger.info(msg=_L("Topic %s has been updated on  %s") % (title, chat_id))
    else:
        logger.error(msg=_L("Error when modifying topic: %s") % result)

    return result


def mute(chat_id=False, user_id=False, extra=""):
    """
    Use API call to have the bot op user in
    :param chat_id:  chat id to locate user into
    :param user_id:  user id to op
    :param extra: permissions to set or 'op'|'deop' for full
    :return:
    """

    logger = logging.getLogger(__name__)
    result = {'ok': False}

    permissions = ["can_send_messages", "can_send_media_messages", "can_send_other_messages", "can_add_web_page_previews"]

    # Enable all restrictions
    if extra == "" or extra == "mute":
        value = False
    elif extra == "unmute":
        value = True
        # Disable all restrictions
        extra = ""

    if chat_id and user_id:
        # Iterate over permissions to set new value
        for item in permissions:
            extra = "%s&%s=%s" % (extra, item, value)

        # For permissions we must assign all of them in a row or it will
        # reset other settings

        url = "%s%s/restrictChatMember?chat_id=%s&user_id=%s&%s" % (stampy.plugin.config.config(key='url'), stampy.plugin.config.config(key='token'), chat_id, user_id, extra)

        try:
            result = json.load(urllib.urlopen(url))
        except:
            result = {'ok': False}

        if result['ok'] is True or result['ok'] == 'True':
            logger.info(msg=_L("User %s has updated restrictions: %s on %s") % (user_id, item, chat_id))
        else:
            logger.error(msg=_L("Error when modifying user restriction: %s: %s") % (item, result))

    else:
        result = {'ok': False}

    return result


def opall(chat_id=False, extra=""):
    """
    Give op/deop to all users
    :param chat_id:  chat id to locate user into
    :param extra: permissions to set or 'op'|'deop' for full
    :return:
    """

    result = False
    if chat_id:
        for user in stampy.plugin.stats.getusers(chat_id=chat_id):
            newresult = op(chat_id=chat_id, user_id=user, extra=extra)
            # Append all results
            result = result and newresult
    return result


def whois(chat_id=False, user_id=False):
    """
    Use API call to retrieve userid
    :param chat_id:  chat id to locate user into
    :param user_id:  user id to kick out of chat
    :return: API information
    """

    logger = logging.getLogger(__name__)
    result = {'ok': False}

    if chat_id and user_id:
        url = "%s%s/getChatMember?chat_id=%s&user_id=%s" % (stampy.plugin.config.config(key='url'), stampy.plugin.config.config(key='token'), chat_id, user_id)
        try:
            result = json.load(urllib.urlopen(url))
        except:
            result = {'ok': False}
    else:
        result = {'ok': False}

    if result['ok'] is True or result['ok'] == 'True':
        logger.info(msg=_L("User %s information: %s") % (user_id, result['result']))
    else:
        logger.error(msg=_L("Error /whois on user: %s") % result)

    return result
