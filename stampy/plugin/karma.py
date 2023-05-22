#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing karma commands
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import datetime
import logging

from prettytable import from_db_cursor

import stampy.plugin.alias
import stampy.plugin.config
import stampy.stampy
from stampy.i18n import _
from stampy.i18n import _L


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """

    stampy.stampy.cronme(name="karma", interval=24 * 60)

    return ["++", "--", u"—", "@", "^rank", "^srank", "^skarma", "==", "!="]


def cron():
    """
    Function to be executed periodically
    :return:
    """

    dokarmacleanup()


def run(message):    # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    if text := stampy.stampy.getmsgdetail(message)["text"]:
        karmacommands(message)
        karmawords(message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = _("Use `word++` or `word--` to increment or decrement karma, a new message will be sent providing the new total\n\n")
    commandtext += _("Reply to a message with `++`, `--` to give user karma to telegram alias or `==` to repeat karma to the same words or `!=` to invert it\n")
    commandtext += _("Use `rank <word>` or `rank` to get value for actual word or top 10 rankings\n")
    commandtext += _("Use `srank <word>` to search for similar words already ranked\n\n")
    if stampy.stampy.is_owner(message):
        commandtext += _("Use `skarma <word>=<value>` to establish karma of a word\n\n")
        commandtext += _("Use `skarma purge` to clear old karma\n\n")

    return commandtext


def karmacommands(message):
    """
    Finds for commands affecting karma in messages
    :param message: message to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]

    # Process lines for commands in the first
    # word of the line (Telegram commands)
    word = texto.split()[0].lower()
    commandtext = False

    # Check first word for commands
    for case in stampy.stampy.Switch(word):
        if case('rank'):
            try:
                word = texto.split()[1]
            except:
                word = False
            commandtext = rank(word, gid=stampy.stampy.geteffectivegid(gid=chat_id))
            break
        if case('srank'):
            try:
                word = texto.split()[1]
            except:
                word = False
            commandtext = srank(word, gid=stampy.stampy.geteffectivegid(gid=chat_id))
            break
        if case('skarma'):
            try:
                word = texto.split()[1]
            except:
                word = False
            if "=" in word:
                key = stampy.plugin.alias.getalias(word=word.split('=')[0], gid=stampy.stampy.geteffectivegid(gid=chat_id))
                value = texto.split('=')[1:][0]
                text = _("Setting karma for `%s` to `%s`") % (key, value)
                stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                                          reply_to_message_id=message_id,
                                          disable_web_page_preview=True,
                                          parse_mode="Markdown")
                putkarma(word=key, value=value, gid=stampy.stampy.geteffectivegid(gid=chat_id))
            elif word == "purge":
                dokarmacleanup()
            break
        if case():
            commandtext = False

    # If any of above cases did a match, send command
    if commandtext:
        stampy.stampy.sendmessage(chat_id=chat_id, text=commandtext,
                                  reply_to_message_id=message_id,
                                  parse_mode="Markdown")
        logger.debug(msg=f"karmacommand:  {word}")
    return


def rank(word=False, gid=0):
    """
    Outputs rank for word or top 10
    :param gid: Group ID to filter
    :param word: word to return rank for
    :return:
    """

    logger = logging.getLogger(__name__)
    if word:

        # if word is provided, return the rank value for that word

        if stampy.plugin.alias.getalias(word, gid=gid):
            word = stampy.plugin.alias.getalias(word, gid=gid)

        string = (word, gid)
        sql = "SELECT word,value,date FROM karma WHERE word='%s' and gid='%s';" % string
        cur = stampy.stampy.dbsql(sql)
        value = cur.fetchone()

        try:
            # Get value from SQL query
            value = value[1]

        except:
            # Value didn't exist before, return 0 value
            value = 0
        text = _("`%s` has `%s` karma points.") % (word, value)

    else:
        # if word is not provided, return top 10 words with top karma
        sql = f"select word,value,date from karma where gid='{gid}' ORDER BY value DESC LIMIT 10;"

        text = _("Global rankings:\n")
        cur = stampy.stampy.dbsql(sql)
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg=_L("Returning karma %s for word %s") % (text, word))
    return text


def srank(word=False, gid=0):
    """
    Search for rank for word
    :param gid: Group ID to filter
    :param word: word to search in database
    :return: table with the values for srank
    """
    logger = logging.getLogger(__name__)
    if stampy.plugin.alias.getalias(word, gid=gid):
        word = stampy.plugin.alias.getalias(word, gid=gid)
    text = ""
    if word is False:
        # If no word is provided to srank, call rank instead
        text = rank(word)
    else:
        string = f"%{word}%"
        sql = f"SELECT word,value,date FROM karma WHERE word LIKE '{string}' AND gid='{gid}' LIMIT 10;"
        cur = stampy.stampy.dbsql(sql)
        table = from_db_cursor(cur)
        text = "%s\n```%s```" % (text, table.get_string())
    logger.debug(msg=_L("Returning srank for word: %s") % word)
    return text


def updatekarma(word=False, change=0, gid=0):
    """
    Updates karma for a word
    :param gid: Group ID to filter
    :param word:  Word to update
    :param change:  Change in karma
    :return:
    """

    logger = logging.getLogger(__name__)
    value = getkarma(word=word, gid=gid) + change
    putkarma(word, value, gid=gid)
    logger.debug(msg=_L("Putting karma of %s to %s") % (value, word))
    return value


def getkarma(word, gid=0):
    """
    Gets karma for a word
    :param gid: Group ID to filter
    :param word: word to get karma for
    :return: karma of given word
    """

    logger = logging.getLogger(__name__)
    string = (word, gid)
    sql = "SELECT word,value FROM karma WHERE word='%s' AND gid='%s';" % string
    cur = stampy.stampy.dbsql(sql)
    value = cur.fetchone()

    try:
        # Get value from SQL query
        value = int(value[1])

    except:
        # Value didn't exist before, return 0
        value = 0
    logger.debug(msg=_L("Getting karma for %s: %s") % (word, value))
    return value


def putkarma(word, value, gid=0):
    """
    Updates value of karma for a word
    :param gid: Group ID to filter
    :param word: Word to update
    :param value: Value of karma to set
    :return: sql execution
    """

    logger = logging.getLogger(__name__)
    date = datetime.datetime.now()
    datefor = date.strftime('%Y-%m-%d %H:%M:%S')

    sql = f"DELETE FROM karma WHERE word = '{word}' AND gid='{gid}';"
    stampy.stampy.dbsql(sql)
    if value != 0:
        sql = f"INSERT INTO karma(word,value,date,gid) VALUES('{word}','{value}', '{datefor}', '{gid}');"
        stampy.stampy.dbsql(sql)

    logger.debug(msg=_L("Putting karma of %s to %s") % (value, word))
    return


def stampyphant(chat_id="", karma=0):
    """
    Returns a sticker for big karma values
    :param chat_id:
    :param karma:
    :return:
    """

    logger = logging.getLogger(__name__)
    karma = f"{karma}"
    # Sticker definitions for each rank
    x00 = "BQADBAADYwAD17FYAAEidrCCUFH7AgI"
    x000 = "BQADBAADZQAD17FYAAEeeRNtkOWfBAI"
    x0000 = "BQADBAADZwAD17FYAAHHuNL2oLuShwI"
    sticker = ""
    if karma[-5:] == "00000":
        x00000 = "BQADBAADaQAD17FYAAHzIBRZeY4uNAI"

        sticker = x00000
    elif karma[-4:] == "0000":
        sticker = x0000
    elif karma[-3:] == "000":
        sticker = x000
    elif karma[-2:] == "00":
        sticker = x00

    text = _("Sticker for %s karma points") % karma

    if sticker != "":
        stampy.stampy.sendsticker(chat_id=chat_id, sticker=sticker, text=f"{text}")
        logger.debug(msg=text)
    return


def karmawords(message):
    """
    Finds for commands affecting karma in messages
    :param message: message to process
    :return:
    """
    karmaprocess(stampy.stampy.getmsgdetail(message))
    return


def karmaprocess(msgdetail):
    """
    Processes karma operators in text
    :param msgdetail: message details as per getmsgdetail
    :return:
    """

    logger = logging.getLogger(__name__)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]
    who_gn = msgdetail["who_gn"]
    who_id = msgdetail["who_id"]
    who_ln = msgdetail["who_ln"]
    gid = stampy.stampy.geteffectivegid(gid=chat_id)

    # Define dictionary for text replacements
    dictionary = {
        "'": "",
        "@": "",
        "\n": " ",
        u"—": "--"
    }

    if not msgdetail["error"] and texto:
        # Search for telegram commands and if any disable text processing
        text_to_process = stampy.stampy.replace_all(texto,
                                                    dictionary).lower().split(
            " ")
    else:
        text_to_process = ""

    logger.debug(msg=_L("Text to process: %s") % " ".join(text_to_process))

    wordadd = []
    worddel = []

    # Pre-process text for "==" and "!="
    if msgdetail['replytotext']:
        if "==" in " ".join(text_to_process):
            newtext = stampy.stampy.replace_all(msgdetail['replytotext'], dictionary).lower().split(" ")
            text_to_process.extend(newtext)
        elif "!=" in " ".join(text_to_process):
            newdictionary = {
                "++": "+-",
                "--": "-+"
            }

            newtext = stampy.stampy.replace_all(msgdetail['replytotext'], newdictionary).lower().split(" ")

            # Finish inversion
            newdictionary = {
                "+-": "--",
                "-+": "++"
            }

            newtext = stampy.stampy.replace_all(" ".join(newtext), newdictionary).lower().split(" ")
            text_to_process = newtext

    # If operators are not there, exit faster
    if "--" in " ".join(text_to_process) or "++" in " ".join(text_to_process):
        logger.debug(msg=_L("Text has karma operators"))
        for word in text_to_process:
            if "++" in word or "--" in word:
                msg = _("Processing word %s sent by id %s with username %s (%s %s)") % (
                    word, who_id, who_un, who_gn, who_ln)
                logger.debug(msg)

                # This should help to avoid duplicate karma operations
                # in the same message

                oper = False

                if len(word) >= 4:
                    oper = word[-2:]
                    word = word[:-2]
                elif len(word) == 2:
                    oper = word[-2:]
                    try:
                        word = msgdetail["replyto"].lower()
                    except:
                        word = False

                if word and oper:
                    if stampy.plugin.alias.getalias(word, gid=gid):
                        word = stampy.plugin.alias.getalias(word, gid=gid).split(" ")
                    for item in word:
                        if stampy.plugin.alias.getalias(item, gid=gid):
                            item = stampy.plugin.alias.getalias(item, gid=gid)
                        if oper == "++" and item not in wordadd:
                            wordadd.append(item)
                        if oper == "--" and item not in worddel:
                            worddel.append(item)

    messagetext = ""
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
            msg = _("%s Found in %s at %s with id %s (%s), sent by id %s named %s (%s %s)") % (oper, word, chat_id, message_id, msgdetail["chat_name"], who_id, who_un, who_gn, who_ln)
            logger.debug(msg)

            karma = updatekarma(word=word, change=change, gid=stampy.stampy.geteffectivegid(gid=chat_id))
            if karma != 0:
                # Karma has changed, report back
                text = _("`%s` now has `%s` karma points.") % (word, karma)
            else:
                # New karma is 0
                text = _("`%s` now has no Karma and has been garbage collected.") % word

            # Send originating user for karma change a reply with
            # the new value

            modulo = int(stampy.plugin.config.gconfig(key="modulo", default="1", gid=chat_id))

            if modulo != 0:
                if karma % modulo == 0:
                    messagetext = messagetext + "\n" + text
            stampyphant(chat_id=chat_id, karma=karma)

    if messagetext != "":
        stampy.stampy.sendmessage(chat_id=chat_id, text=messagetext, reply_to_message_id=message_id, parse_mode="Markdown")

    return


def dokarmacleanup(word=False, maxage=int(stampy.plugin.config.config("maxage", default=180))):
    """
    Checks on the karma database the date of the last update in the word
    :param word: word to query in database
    :param maxage: defines maximum number of days to allow karma to be inactive
    """

    logger = logging.getLogger(__name__)

    if word:
        sql = f"SELECT word,value,date FROM karma WHERE word={word}"
    else:
        sql = "SELECT word,value,date,gid FROM karma"

    words = []
    cur = stampy.stampy.dbsql(sql)

    logger.debug(msg=_L("Processing words for cleanup: %s") % words)

    for row in cur:
        # Process each word returned
        word = row[0]
        date = row[2]
        gid = row[3]

        if date and (date != "False"):
            worddate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        else:
            worddate = datetime.datetime.now()

        now = datetime.datetime.now()

        if (now - worddate).days > maxage:
            logger.debug(msg=_L("Word %s with %s inactivity days is going to be purged") % (word, (now - worddate).days))
            words.append({'word': word, 'gid': gid})

    for old in words:
        # Remove word from database based on prior loop
        putkarma(word=old['word'], value=0, gid=old['gid'])
    return
