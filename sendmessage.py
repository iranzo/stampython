#!/usr/bin/env python
# encoding: utf-8
#
# Description: Sends a message to a chatID via CLI
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)


import argparse
from stampy.stampy import sendmessage


description = 'Sends a message using bot to chatid'

# Option parsing
p = argparse.ArgumentParser("sendmessage.py [arguments]", description=description)
p.add_argument("-i", "--id", dest="chat_id", help="chat_id to send message to", default=False)
p.add_argument("-t", "--text", dest="texto", help="Text to send", default=False)

options, unknown = p.parse_known_args()

if options.texto and options.chat_id:
    sendmessage(chat_id=options.chat_id, text=options.texto)
