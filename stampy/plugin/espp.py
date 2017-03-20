#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing essp gain
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging

import stampy.plugin.config
import stampy.plugin.stock
import stampy.stampy


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    return "/espp"


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower() == "/espp":
            espp(message=message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = "Use `/espp <amount>` to get estimated espp earnings\n\n"
    return commandtext


def espp(message):
    """
    Processes espp commands
    :param message: Message with the command
    :return:
    """

    logger = logging.getLogger(__name__)
    c = stampy.plugin.stock.GoogleFinanceAPI()
    d = stampy.plugin.stock.CurrencyConverter()

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger.debug(msg="Command: %s by %s" % (texto, who_un))

    # We might be have been given no command, just stock
    try:
        monthly = float(texto.split(' ')[1])
    except:
        monthly = 0

    ticker = stampy.plugin.config.config("stock")

    text = "```\n"
    rate = d.convert("USD", "EUR")
    text += "USD/EUR rate " + str(rate) + "\n"
    initial = float(stampy.plugin.config.config("espp", 0))
    text += "Initial quote: %s USD\n" % initial
    try:
        quote = c.get(ticker)
        final = float(quote["l_cur"])
        text += "Actual quote: %s USD\n" % final
    except:
        final = initial
        text += ""

    if initial > final:
        pricebuy = final
    else:
        pricebuy = initial

    reduced = 0.85 * pricebuy

    text += "Buy price: %s USD\n" % reduced
    text += "Earning per unit: %s USD\n" % (final - reduced)
    if monthly:
        stocks = float(int((monthly / rate) * 6 / reduced))
        text += "Estimated stocks: %s\n" % stocks
        earning = (final - reduced) * stocks * rate
        text += "Estimated earning: %s EUR\n" % "{0:.2f}".format(earning)
        total = monthly * 6 + earning
        text += "Total amount deposited on sell: %s EUR\n" % "{0:.2f}".format(total)
        text += "Estimated A.E.R. vs investment: %s %%" % "{0:.2f}".format(earning / (total - earning) * 100)

    text += "```"
    logger.debug(msg=text)
    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                              reply_to_message_id=message_id,
                              disable_web_page_preview=True,
                              parse_mode="Markdown")
