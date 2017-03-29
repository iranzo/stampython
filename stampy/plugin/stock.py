#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing stock requests
# Author: Javier Ramirez Molina (javilinux@gmail.com)
# URL: https://github.com/javilinux/StockCurrency/blob/master/StockCurrency.py
# Modified by: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import json
import logging
import urllib2
import requests

import stampy.stampy
import stampy.plugin.config
from stampy.i18n import _


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    return "stock"


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower() == "stock":
            stock(message=message)
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = _("Use `stock <ticker>` to get stock trading price\n\n")
    return commandtext


class CurrencyConverter:
    def __init__(self):
        self.prefix = "http://themoneyconverter.com/"

    def convert(self, currencyf, currencyt):
        url = self.prefix + currencyf + "/" + currencyt + ".aspx"
        # split and strip
        split1 = ': 1 %s = ' % 'United States Dollar'
        strip1 = ' %s</h3>' % 'Euro'

        rate = requests.get(url)
        a = float(rate.text.split(split1)[1].split(strip1)[0].strip())
        return a


class GoogleFinanceAPI:
    def __init__(self):
        self.prefix = "http://finance.google.com/finance/info?client=ig&q="

    def get(self, symbol, exchange=False):
        string = ""
        if symbol and exchange:
            string = "%s:%s" % (exchange, symbol)
        if symbol and not exchange:
            string = "%s" % symbol
        url = self.prefix + "%s" % string
        u = urllib2.urlopen(url)
        content = u.read()

        obj = json.loads(content[3:])
        return obj[0]


def stock(message):
    """
    Processes stock commands
    :param message: Message with the command
    :return:
    """

    logger = logging.getLogger(__name__)
    c = GoogleFinanceAPI()
    d = CurrencyConverter()

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger.debug(msg="Command: %s by %s" % (texto, who_un))

    # We might be have been given no command, just stock
    try:
        command = texto.split(' ')[1]
    except:
        command = False

    if not command:
        stock = stampy.plugin.config.config("stock", "RHT").split(" ")
    else:
        stock = texto.split(" ")[1::]

    text = "```\n"
    rate = d.convert("USD", "EUR")
    text += _("USD/EUR rate " + str(rate) + "\n")
    for ticker in stock:
        try:
            quote = c.get(ticker)
            text += "%s Quote " % quote["t"] + " " + quote["l_cur"] + " " + quote["c"] + " (%s%%)" % quote["cp"]
            quoteUSD = float(quote["l_cur"])
            quoteEur = float(quoteUSD * rate)
            text += " (%s EUR)\n" % "{0:.2f}".format(quoteEur)
        except:
            text += ""

    text += "```"
    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                              reply_to_message_id=message_id,
                              disable_web_page_preview=True,
                              parse_mode="Markdown")
