#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for forwarding messages
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import json
import logging
import urllib
from time import sleep

from apscheduler.schedulers.background import BackgroundScheduler

import stampy.plugin.config
import stampy.stampy

sched = BackgroundScheduler()
sched.start()


def init():
    """
    Initializes module
    :return:
    """

    return


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    logger.debug(msg="Origin Chatid: %s, Forward Source: %s" % (msgdetail["chat_id"], str(stampy.plugin.config.config('forwardsource', "")).split()))
    if str(msgdetail["chat_id"]) in str(stampy.plugin.config.config('forwardsource', "")).split():
        for chat_id in str(stampy.plugin.config.config('forwardtarget', "")).split():
            logger.debug(msg="Origin chatid: %s, Forward Target: %s" % (msgdetail["chat_id"], str(stampy.plugin.config.config('forwardtarget', "")).split()))
            forwardmessage(message=message, target_chatid=chat_id)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """

    commandtext = ""
    if stampy.plugin.config.config(key='owner') == stampy.stampy.getmsgdetail(message)["who_un"]:
        commandtext += "Set source and target chats with forwardsource and forwardtarget with ids of chats"
    return commandtext


def forwardmessage(message, target_chatid, disable_notification=False):

    logger = logging.getLogger(__name__)
    msgdetail = stampy.stampy.getmsgdetail(message)

    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]

    url = "%s%s/forwardMessage" % (stampy.plugin.config.config(key="url"),
                                   stampy.plugin.config.config(key='token'))

    message = "%s?chat_id=%s&from_chat_id=%s&message_id=%s" % (
        url, target_chatid, chat_id, message_id)
    if disable_notification:
        message += "&disable_notification=%s" % disable_notification

    code = False
    attempt = 0
    while not code:
        result = json.load(urllib.urlopen(message))
        code = result['ok']
        logger.error(msg="ERROR (%s) forwarding message: Code: %s : Text: %s" % (
            attempt, code, result))
        attempt = attempt + 1
        sleep(1)
        # exit after 60 retries with 1 second delay each
        if attempt > 60:
            logger.error(msg="PERM ERROR forwarding message: Code: %s : Text: "
                             "%s" % (code, result))
            code = True
    logger.debug(msg="forwarding message: Code: %s : Text: %s" % (code, message))
    return
