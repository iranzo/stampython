#!/usr/bin/env python
# encoding: utf-8

import logging
from unittest import TestCase

import cleanup
import stampy.plugin.alias
import stampy.plugin.karma
import stampy.stampy

logger = logging.getLogger(__name__)


class TestStampy(TestCase):
    cleanup.clean()

    def test_kick(self):
        true = True
        messages = [{"update_id": 240168933,
                     "message": {"message_id": 4831,
                                 "from": {"id": 5812695, "first_name": "Pablo", "last_name": "Iranzo G\u00f3mez",
                                          "username": "iranzo", "language_code": "es"},
                                 "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                          "all_members_are_administrators": true}, "date": 1497476585,
                                 "reply_to_message": {"message_id": 4830, "from": {"id": 5812695, "first_name": "Pablo",
                                                                                   "last_name": "Iranzo G\u00f3mez",
                                                                                   "username": "iranzo",
                                                                                   "language_code": "es"},
                                                      "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                                               "all_members_are_administrators": true},
                                                      "date": 1497476576, "text": "test"}, "text": "/kick"}}]

        stampy.stampy.process(messages)

    def test_whois(self):
        true = True
        messages = [{"update_id": 240168933,
                     "message": {"message_id": 4831,
                                 "from": {"id": 5812695, "first_name": "Pablo", "last_name": "Iranzo G\u00f3mez",
                                          "username": "iranzo", "language_code": "es"},
                                 "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                          "all_members_are_administrators": true}, "date": 1497476585,
                                 "reply_to_message": {"message_id": 4830, "from": {"id": 5812695, "first_name": "Pablo",
                                                                                   "last_name": "Iranzo G\u00f3mez",
                                                                                   "username": "iranzo",
                                                                                   "language_code": "es"},
                                                      "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                                               "all_members_are_administrators": true},
                                                      "date": 1497476576, "text": "test"}, "text": "/whois"}}]

        stampy.stampy.process(messages)

    def test_deopall(self):
        true = True
        messages = [{"update_id": 240168933,
                     "message": {"message_id": 4831,
                                 "from": {"id": 5812695, "first_name": "Pablo", "last_name": "Iranzo G\u00f3mez",
                                          "username": "iranzo", "language_code": "es"},
                                 "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                          "all_members_are_administrators": true}, "date": 1497476585,
                                 "reply_to_message": {"message_id": 4830, "from": {"id": 5812695, "first_name": "Pablo",
                                                                                   "last_name": "Iranzo G\u00f3mez",
                                                                                   "username": "iranzo",
                                                                                   "language_code": "es"},
                                                      "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                                               "all_members_are_administrators": true},
                                                      "date": 1497476576, "text": "test"}, "text": "/deopall"}}]

        stampy.stampy.process(messages)

    def test_opall(self):
        true = True
        messages = [{"update_id": 240168933,
                     "message": {"message_id": 4831,
                                 "from": {"id": 5812695, "first_name": "Pablo", "last_name": "Iranzo G\u00f3mez",
                                          "username": "iranzo", "language_code": "es"},
                                 "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                          "all_members_are_administrators": true}, "date": 1497476585,
                                 "reply_to_message": {"message_id": 4830, "from": {"id": 5812695, "first_name": "Pablo",
                                                                                   "last_name": "Iranzo G\u00f3mez",
                                                                                   "username": "iranzo",
                                                                                   "language_code": "es"},
                                                      "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                                               "all_members_are_administrators": true},
                                                      "date": 1497476576, "text": "test"}, "text": "/opall"}}]

        stampy.stampy.process(messages)

    def test_mute(self):
        true = True
        messages = [{"update_id": 240168933,
                     "message": {"message_id": 4831,
                                 "from": {"id": 5812695, "first_name": "Pablo", "last_name": "Iranzo G\u00f3mez",
                                          "username": "iranzo", "language_code": "es"},
                                 "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                          "all_members_are_administrators": true}, "date": 1497476585,
                                 "reply_to_message": {"message_id": 4830, "from": {"id": 5812695, "first_name": "Pablo",
                                                                                   "last_name": "Iranzo G\u00f3mez",
                                                                                   "username": "iranzo",
                                                                                   "language_code": "es"},
                                                      "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                                               "all_members_are_administrators": true},
                                                      "date": 1497476576, "text": "test"}, "text": "/mute"}}]

        stampy.stampy.process(messages)

    def test_unmute(self):
        true = True
        messages = [{"update_id": 240168933,
                     "message": {"message_id": 4831,
                                 "from": {"id": 5812695, "first_name": "Pablo", "last_name": "Iranzo G\u00f3mez",
                                          "username": "iranzo", "language_code": "es"},
                                 "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                          "all_members_are_administrators": true}, "date": 1497476585,
                                 "reply_to_message": {"message_id": 4830, "from": {"id": 5812695, "first_name": "Pablo",
                                                                                   "last_name": "Iranzo G\u00f3mez",
                                                                                   "username": "iranzo",
                                                                                   "language_code": "es"},
                                                      "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                                               "all_members_are_administrators": true},
                                                      "date": 1497476576, "text": "test"}, "text": "/unmute"}}]

        stampy.stampy.process(messages)

    def test_topic(self):
        true = True
        messages = [{"update_id": 240168933,
                     "message": {"message_id": 4831,
                                 "from": {"id": 5812695, "first_name": "Pablo", "last_name": "Iranzo G\u00f3mez",
                                          "username": "iranzo", "language_code": "es"},
                                 "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                          "all_members_are_administrators": true}, "date": 1497476585,
                                 "reply_to_message": {"message_id": 4830, "from": {"id": 5812695, "first_name": "Pablo",
                                                                                   "last_name": "Iranzo G\u00f3mez",
                                                                                   "username": "iranzo",
                                                                                   "language_code": "es"},
                                                      "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                                               "all_members_are_administrators": true},
                                                      "date": 1497476576, "text": "test"}, "text": "/topic test channel"}}]

        stampy.stampy.process(messages)

    def test_deop(self):
        true = True
        messages = [{"update_id": 240168933,
                     "message": {"message_id": 4831,
                                 "from": {"id": 5812695, "first_name": "Pablo", "last_name": "Iranzo G\u00f3mez",
                                          "username": "iranzo", "language_code": "es"},
                                 "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                          "all_members_are_administrators": true}, "date": 1497476585,
                                 "reply_to_message": {"message_id": 4830, "from": {"id": 5812695, "first_name": "Pablo",
                                                                                   "last_name": "Iranzo G\u00f3mez",
                                                                                   "username": "iranzo",
                                                                                   "language_code": "es"},
                                                      "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                                               "all_members_are_administrators": true},
                                                      "date": 1497476576, "text": "test"}, "text": "/deop"}}]

        stampy.stampy.process(messages)

    def test_op(self):
        true = True
        messages = [{"update_id": 240168933,
                     "message": {"message_id": 4831,
                                 "from": {"id": 5812695, "first_name": "Pablo", "last_name": "Iranzo G\u00f3mez",
                                          "username": "iranzo", "language_code": "es"},
                                 "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                          "all_members_are_administrators": true}, "date": 1497476585,
                                 "reply_to_message": {"message_id": 4830, "from": {"id": 5812695, "first_name": "Pablo",
                                                                                   "last_name": "Iranzo G\u00f3mez",
                                                                                   "username": "iranzo",
                                                                                   "language_code": "es"},
                                                      "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                                               "all_members_are_administrators": true},
                                                      "date": 1497476576, "text": "test"}, "text": "/op"}}]

        stampy.stampy.process(messages)

    def test_unban(self):
        true = True
        messages = [{"update_id": 240168933,
                     "message": {"message_id": 4831,
                                 "from": {"id": 5812695, "first_name": "Pablo", "last_name": "Iranzo G\u00f3mez",
                                          "username": "iranzo", "language_code": "es"},
                                 "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                          "all_members_are_administrators": true}, "date": 1497476585,
                                 "reply_to_message": {"message_id": 4830, "from": {"id": 5812695, "first_name": "Pablo",
                                                                                   "last_name": "Iranzo G\u00f3mez",
                                                                                   "username": "iranzo",
                                                                                   "language_code": "es"},
                                                      "chat": {"id": -158164217, "title": "BOTdevel", "type": "group",
                                                               "all_members_are_administrators": true},
                                                      "date": 1497476576, "text": "test"}, "text": "/unban"}}]

        stampy.stampy.process(messages)
