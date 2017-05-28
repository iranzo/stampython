#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing admin commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging
import random
import string

from prettytable import from_db_cursor

import stampy.plugin.config
import stampy.stampy
from stampy.i18n import _
from stampy.i18n import _L


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    triggers = ["^/admin"]
    return triggers


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text and stampy.stampy.is_owner_or_admin(message):
        if text.split()[0].lower()[0:6] == "/admin":
            admincommands(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    if stampy.stampy.is_owner_or_admin(message):
        commandtext += _("Use `/admin unlink` to remove channel linking\n")
        commandtext += _("Use `/admin link master` to generate and store linking token to be used on slaves\n")
        commandtext += _("Use `/admin link slave <token> to use provided token to link against master channel\n")
        commandtext += _("Use `/admin link show to list linked channel\n")
    return commandtext


def admincommands(message):
    """
    Processes link commands in the message
    :param message: message to process
    :return:
    """
    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    who_un = msgdetail["who_un"]

    logger = logging.getLogger(__name__)

    # Only users defined as 'owner' or 'admin' can perform commands
    if stampy.stampy.is_owner_or_admin(message):
        logger.debug(msg=_L("Command: %s by %s") % (texto, who_un))
        try:
            command = texto.split(' ')[1]
        except:
            command = False

        try:
            word = texto.split(' ')[2]
        except:
            word = ""

        for case in stampy.stampy.Switch(command):
            if case('unlink'):
                chanunlink(message)
                break
            if case('link'):
                if word == "master":
                    changenmastertoken(message=message)
                elif word == "slave":
                    try:
                        token = texto.split(' ')[3]
                        if token:
                            chanlinkslave(message=message, token=token)
                    except:
                        pass
                elif word == "show":
                    chanshowslave(message=message)
                break
            if case():
                break
    return


def changenmastertoken(message):
    """
    Generates Master token for channel
    :param message: Message to process
    :return:
    """

    msgdetail = stampy.stampy.getmsgdetail(message)

    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]

    logger = logging.getLogger(__name__)

    if not stampy.plugin.config.config(key='link', default=False, gid=chat_id):
        if not stampy.plugin.config.config(key='link-master', default=False, gid=chat_id):
            charset = string.letters + string.digits
            size = 20
            token = ''.join((random.choice(charset)) for x in range(size))
            generatedtoken = "%s:%s" % (chat_id, token)
            stampy.plugin.config.setconfig(key='link-master', gid=chat_id,
                                           value=generatedtoken)
            logger.debug(msg=_L("Generated token %s for channel %s") % (token, chat_id))
            text = _("Token for linking against this channel has been generated "
                     "as %s") % generatedtoken
        else:
            generatedtoken = stampy.plugin.config.config(key='link-master', default=False, gid=chat_id)
            logger.debug(msg=_L("Already generated token %s for channel %s") % (generatedtoken, chat_id))
            text = _("A token for linking against this channel already existed as %s") % generatedtoken

        text = text + _("\n\nChannel has also been enabled as running in isolated "
                        "mode, use ```/gconfig delete isolated``` to revert back to "
                        "global karma")
        stampy.plugin.config.setconfig(key='isolated', gid=chat_id, value=True)

    else:
        text = _("This channel is a slave for another one, cannot generate token")

    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                              reply_to_message_id=message_id,
                              disable_web_page_preview=True,
                              parse_mode="Markdown")
    return


def chanlinkslave(message, token=""):
    """
    Link a channel as slave of another and sets relevant configuration
    :param message: Message with the command
    :param token: Extracted token provided on command line
    :return:
    """
    logger = logging.getLogger(__name__)
    msgdetail = stampy.stampy.getmsgdetail(message)

    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]

    masterid = token.split(':')[0]

    logger.debug(msg=_L("chanenslave: %s, master-id: %s, master-token:%s") % (chat_id, masterid, token.split(':')[1]))

    if stampy.plugin.config.config(key='link-master', default=False,
                                   gid=masterid) == token:
        # In master GID, token is the same as the one provided

        # Delete link-master from master
        stampy.plugin.config.deleteconfig(key='link-master', gid=masterid)

        # Define 'link' and 'isolated' on slave
        stampy.plugin.config.setconfig(key='link', gid=chat_id, value=masterid)
        stampy.plugin.config.setconfig(key='isolated', gid=chat_id, value=True)

        # Notify master channel of slave linked
        text = _("Channel *%s* with name *%s* has been linked as *SLAVE*") % (chat_id, msgdetail['chat_name'])

        stampy.stampy.sendmessage(chat_id=masterid, text=text,
                                  disable_web_page_preview=True,
                                  parse_mode="Markdown")

        # Notify slave of master linked

        text = _("This channel has been set as *SLAVE* from *MASTER* channel *%s*") % masterid

        stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                  reply_to_message_id=message_id,
                                  disable_web_page_preview=True,
                                  parse_mode="Markdown")

    return


def chanunlink(message):
    """
    Unlinks channel
    :param message: Message to process
    :return:
    """
    logger = logging.getLogger(__name__)
    msgdetail = stampy.stampy.getmsgdetail(message)

    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    masterid = stampy.plugin.config.config(key='link', default=False, gid=chat_id)

    if masterid:
        # Delete link from slave
        stampy.plugin.config.deleteconfig(key='link', gid=chat_id)

        # Notify master channel of slave linked
        text = _("Channel *%s* with name *%s* has been unlinked as *SLAVE*") % (chat_id, msgdetail['chat_name'])

        stampy.stampy.sendmessage(chat_id=masterid, text=text,
                                  disable_web_page_preview=True,
                                  parse_mode="Markdown")

        # Notify slave of master linked
        text = _("This channel has been unliked as *SLAVE* from *MASTER* channel *%s*") % masterid
        text = text + _("\n\nChannel has also been enabled as running in "
                        "isolated mode, use ```/gconfig delete isolated``` to "
                        "revert back to global karma")

        stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                  reply_to_message_id=message_id,
                                  disable_web_page_preview=True,
                                  parse_mode="Markdown")
    return


def chanshowslave(message):
    """
    Shows slaves associated to current channel
    :param message: Message to process
    :return:
    """
    logger = logging.getLogger(__name__)
    msgdetail = stampy.stampy.getmsgdetail(message)

    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    masterid = stampy.plugin.config.config(key='link', default=False, gid=chat_id)

    if masterid:
        # We've a master channel, report it
        text = _("This channel %s is slave of channel %s") % (chat_id, masterid)
    else:
        # We nee to check database to see if we've any slave
        sql = "SELECT id from config where key='link' and value='%s'" % chat_id
        cur = stampy.stampy.dbsql(sql=sql)

        text = _("Defined slaves:\n")
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())

    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                              reply_to_message_id=message_id,
                              disable_web_page_preview=True,
                              parse_mode="Markdown")
    return
