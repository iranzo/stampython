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

    def test_hilist(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/hilight list',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_hiadd(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/hilight add iranzo',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_hidel(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/hilight del iranzo',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_hinocommand(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/hilight',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)
