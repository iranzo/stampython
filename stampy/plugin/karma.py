#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing karma commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

from prettytable import from_db_cursor

import stampy.plugin.alias
import stampy.stampy
import stampy.plugin.config


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
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        karmacommands(message)
        karmawords(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = "Use `word++` or `word--` to "
    commandtext += "increment or decrement karma, a new message will"
    commandtext += " be sent providing the new total\n\n"
    commandtext += "Use `rank word` or `rank` to get value for actual "
    commandtext += "word or top 10 rankings\n"
    commandtext += "Use `srank word` to search for similar words"
    commandtext += " already ranked\n\n"
    if stampy.plugin.config.config(key='owner') == stampy.stampy.getmsgdetail(message)["who_un"]:
        commandtext += "Use `skarma word=value` " \
                       "to establish karma of a word\n\n"

    return commandtext


def karmacommands(message):
    """
    Finds for commands affecting karma in messages
    :param message: message to process
    :return:
    """

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]

    logger = logging.getLogger(__name__)
    # Process lines for commands in the first
    # word of the line (Telegram commands)
    word = texto.split()[0]
    commandtext = False

    # Check first word for commands
    for case in stampy.stampy.Switch(word):
        if case('rank'):
            try:
                word = texto.split()[1]
            except:
                word = False
            commandtext = rank(word)
            break
        if case('srank'):
            try:
                word = texto.split()[1]
            except:
                word = False
            commandtext = srank(word)
            break
        if case('skarma'):
            try:
                word = texto.split()[1]
            except:
                word = False
            if "=" in word:
                key = word.split('=')[0]
                value = texto.split('=')[1:][0]
                text = "Setting karma for `%s` to `%s`" % (key, value)
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                putkarma(word=key, value=value)
            break
        if case():
            commandtext = False

    # If any of above cases did a match, send command
    if commandtext:
        stampy.stampy.sendmessage(chat_id=chat_id, text=commandtext,
                                  reply_to_message_id=message_id,
                                  parse_mode="Markdown")
        logger.debug(msg="karmacommand:  %s" % word)
    return


def rank(word=False):
    """
    Outputs rank for word or top 10
    :param word: word to return rank for
    :return:
    """

    logger = logging.getLogger(__name__)
    if stampy.plugin.alias.getalias(word):
        word = stampy.plugin.alias.getalias(word)
    if word:
        # if word is provided, return the rank value for that word
        string = (word,)
        sql = "SELECT * FROM karma WHERE word='%s';" % string
        cur = stampy.stampy.dbsql(sql)
        value = cur.fetchone()

        try:
            # Get value from SQL query
            value = value[1]

        except:
            # Value didn't exist before, return 0 value
            value = 0
        text = "`%s` has `%s` karma points." % (word, value)

    else:
        # if word is not provided, return top 10 words with top karma
        sql = "select * from karma ORDER BY value DESC LIMIT 10;"

        text = "Global rankings:\n"
        cur = stampy.stampy.dbsql(sql)
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg="Returning karma %s for word %s" % (text, word))
    return text


def srank(word=False):
    """
    Search for rank for word
    :param word: word to search in database
    :return: table with the values for srank
    """
    logger = logging.getLogger(__name__)
    if stampy.plugin.alias.getalias(word):
        word = stampy.plugin.alias.getalias(word)
    text = ""
    if word is False:
        # If no word is provided to srank, call rank instead
        text = rank(word)
    else:
        string = "%" + word + "%"
        sql = "SELECT * FROM karma WHERE word LIKE '%s' LIMIT 10;" % string
        cur = stampy.stampy.dbsql(sql)
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg="Returning srank for word: %s" % word)
    return text


def updatekarma(word=False, change=0):
    """
    Updates karma for a word
    :param word:  Word to update
    :param change:  Change in karma
    :return:
    """

    # logger = logging.getLogger(__name__)
    value = getkarma(word=word) + change
    putkarma(word, value)
    return value


def getkarma(word):
    """
    Gets karma for a word
    :param word: word to get karma for
    :return: karma of given word
    """

    # logger = logging.getLogger(__name__)
    string = (word,)
    sql = "SELECT * FROM karma WHERE word='%s';" % string
    cur = stampy.stampy.dbsql(sql)
    value = cur.fetchone()

    try:
        # Get value from SQL query
        value = value[1]

    except:
        # Value didn't exist before, return 0
        value = 0

    return value


def putkarma(word, value):
    """
    Updates value of karma for a word
    :param word: Word to update
    :param value: Value of karma to set
    :return: sql execution
    """

    logger = logging.getLogger(__name__)

    sql = "DELETE FROM karma WHERE  word = '%s';" % word
    stampy.stampy.dbsql(sql)
    if value != 0:
        sql = "INSERT INTO karma VALUES('%s','%s');" % (word, value)
        stampy.stampy.dbsql(sql)

    return


def stampyphant(chat_id="", karma=0):
    """
    Returns a sticker for big karma values
    :param chat_id:
    :param karma:
    :return:
    """

    # logger = logging.getLogger(__name__)
    karma = "%s" % karma
    # Sticker definitions for each rank
    x00 = "BQADBAADYwAD17FYAAEidrCCUFH7AgI"
    x000 = "BQADBAADZQAD17FYAAEeeRNtkOWfBAI"
    x0000 = "BQADBAADZwAD17FYAAHHuNL2oLuShwI"
    x00000 = "BQADBAADaQAD17FYAAHzIBRZeY4uNAI"

    sticker = ""
    if karma[-5:] == "00000":
        sticker = x00000
    elif karma[-4:] == "0000":
        sticker = x0000
    elif karma[-3:] == "000":
        sticker = x000
    elif karma[-2:] == "00":
        sticker = x00

    text = "Sticker for %s karma points" % karma

    if sticker != "":
        stampy.stampy.sendsticker(chat_id=chat_id, sticker=sticker, text="%s" % text)
    return


def karmawords(message):
    """
    Finds for commands affecting karma in messages
    :param message: message to process
    :return:
    """

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]

    logger = logging.getLogger(__name__)
    # Process lines for commands in the first
    # word of the line (Telegram commands)
    word = texto.split()[0]

    # Process each word in the line received
    # to search for karma operators

    wordadd = []
    worddel = []

    # Unicode — is sometimes provided by telegram cli,
    # using that also as comparison
    unidecrease = u"—"

    # Define dictionary for text replacements
    dict = {
        "'": "",
        "@": "",
        "\n": " ",
        unidecrease: "--"
    }

    if not msgdetail["error"] and msgdetail["text"]:
        # Search for telegram commands and if any disable text processing
        text_to_process = stampy.stampy.replace_all(msgdetail["text"], dict).lower().split(" ")
    else:
        text_to_process = ""

    for word in text_to_process:
        if "++" in word or "--" in word:
            msg = "Processing word"
            msg += " %s sent by id %s with username %s (%s %s)" % (
                word, msgdetail["who_id"], msgdetail["who_un"], msgdetail["who_gn"], msgdetail["who_ln"])
            logger.debug(msg)

            # This should help to avoid duplicate karma operations
            # in the same message

            if len(word) >= 4:
                oper = word[-2:]
                word = word[:-2]
                if stampy.plugin.alias.getalias(word):
                    word = stampy.plugin.alias.getalias(word).split(" ")
                for item in word:
                    if stampy.plugin.alias.getalias(item):
                        item = stampy.plugin.alias.getalias(item)
                    if oper == "++" and item not in wordadd:
                        wordadd.append(item)
                    if oper == "--" and item not in worddel:
                        worddel.append(item)
    for word in wordadd + worddel:
        change = 0
        oper = False
        if word in wordadd:
            change += 1
            oper = "++"
        if word in worddel:
            change -= 1
            oper = "--"

        if change != 0:
            msg = "%s Found in %s at %s with id %s (%s)," \
                  " sent by id %s named %s (%s %s)" % (
                      oper, word, msgdetail["chat_id"], msgdetail["message_id"],
                      msgdetail["chat_name"], msgdetail["who_id"],
                      msgdetail["who_un"], msgdetail["who_gn"], msgdetail["who_ln"])
            logger.debug(msg)

            karma = updatekarma(word=word, change=change)
            if karma != 0:
                # Karma has changed, report back
                text = "`%s` now has `%s` karma points." % (
                    word, karma)
            else:
                # New karma is 0
                text = "`%s` now has no Karma and has" % word
                text += " been garbage collected."

            # Send originating user for karma change a reply with
            # the new value
            stampy.stampy.sendmessage(chat_id=msgdetail["chat_id"], text=text,
                                      reply_to_message_id=msgdetail["message_id"],
                                      parse_mode="Markdown")
            stampyphant(chat_id=msgdetail["chat_id"], karma=karma)

    return
