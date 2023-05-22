#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing stock requests
# Author: Javier Ramirez Molina (javilinux@gmail.com)
# URL: https://github.com/javilinux/StockCurrency/blob/master/StockCurrency.py
# Modified by: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging
import json
import sys
import requests

import stampy.plugin.config
import stampy.stampy
from stampy.i18n import _
from stampy.i18n import _L


def init():
    """
    Initializes module
    :return: List of triggers for plugin
    """
    return ["^stock"]


def run(message):    # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    if text:
        = stampy.stampy.getmsgdetail(message)["text"]:
        if text.split()[0].lower() == "stock":
            stock(message=message)
    return


def help(message):    # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    return _("Use `stock <ticker>` to get stock trading price\n\n")


class IEXAPI:
    def __init__(self):
        self.prefix = "https://api.iextrading.com/1.0/stock/"

    def get(self, symbol):
        url = f"{self.prefix}{symbol}/quote"
        content = json.loads(requests.get(url).content)
        quote = {'t': symbol}
        if "change" in content:
            quote['c'] = content['change']
        if "changePercent" in content:
            quote['cp'] = content['changePercent'] * 100
        if "latestPrice" in content:
            quote['l_cur'] = content['latestPrice']
        return quote


def get_currency_rate(currency, rate_in):
    """
    Get currency rate
    :param currency: Original Currency
    :param rate_in: Destination Currency
    :return: rate
    """

    stockapikey = stampy.plugin.config.config(key="stockapikey", default="")

    base_url = 'http://data.fixer.io/api/latest?access_key=%s' % stockapikey

    query = base_url + '&symbols=%s' % currency

    try:
        response = requests.get(query)
        if response.status_code != 200:
            response = 'N/A'
            return response
        else:
            rates = response.json()
            if 'rates' in rates:
                rate_in_currency = 1 / rates["rates"][currency]
            else:
                rate_in_currency = 1
            return rate_in_currency
    except requests.ConnectionError as error:
        print error
        sys.exit(1)


def stock(message):
    """
    Processes stock commands
    :param message: Message with the command
    :return:
    """

    logger = logging.getLogger(__name__)
    c = IEXAPI()

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger.debug(msg=_L(f"Command: {texto} by {who_un}"))

    # We might be have been given no command, just stock
    try:
        command = texto.split(' ')[1]
    except:
        command = False

    if not command:
        stock = stampy.plugin.config.gconfig(
            key="stock", default="RHT", gid=chat_id).split(" ")
    else:
        stock = texto.split(" ")[1::]

    text = "```\n"
    currency = stampy.plugin.config.gconfig(
        key="currency", default="EUR", gid=chat_id)
    rate = get_currency_rate('USD', currency) if currency != 'USD' else 1
    text += _(f"USD/{currency} rate {str(rate)}" + "\n")
    for ticker in stock:
        try:
            quote = c.get(ticker.upper())
            text += (
                f'{quote["t"]} Quote  '
                + str(quote["l_cur"])
                + " "
                + str(quote["c"])
                + " (%s%%)" % str(quote["cp"])
            )
            quoteUSD = quote["l_cur"]
            quoteEur = float(quoteUSD * rate)
            text += " (%s %s)\n" % ("{0:.2f}".format(quoteEur), currency)
        except:
            text += ""

    text += "```"
    stampy.stampy.sendmessage(chat_id=chat_id, text=text,
                              reply_to_message_id=message_id,
                              disable_web_page_preview=True,
                              parse_mode="Markdown")
