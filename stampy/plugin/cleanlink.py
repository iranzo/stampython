#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for expanding short urls and cleaning up links with tags
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

import re
import requests
import stampy.stampy
import stampy.plugin.config
from stampy.i18n import _
from stampy.i18n import _L


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """

    return ["*"]


def cron():
    """
    Function to be executed periodically
    :return:
    """


def run(message):    # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_id = msgdetail["who_id"]
    newtexto = ""
    delete = False

    cleanlink = stampy.plugin.config.config(key='cleanlink', gid=chat_id)
    cleankey = stampy.plugin.config.config(key='cleankey', gid=chat_id)

    if cleanlink and 'http' in texto:
        newtexto = _("Cleaned up: ")
        for word in texto.split():
            if "http" in word:
                url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', word)
                if len(url) != 0:
                    url = url[0]

                    # Unshorten URL
                    try:
                        session = requests.Session()  # so connections are recycled
                        resp = session.head(url, allow_redirects=True)
                        newurl = resp.url
                    except:
                        # Fake as we couldn't expand url
                        newurl = url

                    if newurl != url:
                        delete = True

                    # Check if url has to be cleaned
                    if cleankey:
                        renewurl = re.sub(cleankey, '', newurl)
                        if renewurl != newurl:
                            delete = True

                        newurl = renewurl

                    newtexto = f"{newtexto} {newurl}"
            else:
                newtexto = f"{newtexto} {word}"

    if delete:
        logger.info(f"Link cleaner for {who_id} in chat {chat_id}")
        stampy.stampy.sendmessage(chat_id=chat_id, text=newtexto,
                                  reply_to_message_id=message_id,
                                  disable_web_page_preview=False)

        # Attempt to delete initial message
        stampy.stampy.deletemessage(chat_id=chat_id, message_id=message_id)

    return


def help(message):    # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    return ""
