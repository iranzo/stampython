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

    def test_welcome(self):
        true = True
        messages = [{"update_id": 240168933,
                     "message": {"message_id": 4829,
                                 "from": {"id": 5812695, "first_name": "Pablo",
                                          "last_name": "Iranzo G\u00f3mez",
                                          "username": "iranzo", "language_code": "es"},
                                 "chat": {"id": -158164217, "title": "BOTdevel",
                                          "type": "group",
                                          "all_members_are_administrators": true},
                                 "date": 1497476575,
                                 "new_chat_participant": {"id": 279488169,
                                                          "first_name": "stampytest_bot",
                                                          "username": "stampytest_bot"},
                                 "new_chat_member": {"id": 279488169,
                                                     "first_name": "stampytest_bot",
                                                     "username": "stampytest_bot"},
                                 "new_chat_members": [
                                     {"id": 279488169, "first_name": "stampytest_bot",
                                      "username": "stampytest_bot"}]}}]
        stampy.stampy.process(messages)
