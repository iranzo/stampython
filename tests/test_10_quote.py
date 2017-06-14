#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import stampy.plugin.quote


class TestStampy(TestCase):
    def test_addquote(self):
        # Last row was 0 before insert
        self.assertEqual(stampy.plugin.quote.addquote('iranzo', 'now', 'Test'), 0)

    def test_getquote(self):
        self.assertEqual(stampy.plugin.quote.getquote(),
                         (1, 'iranzo', 'now', 'Test'))

    def test_removequote(self):
        stampy.plugin.quote.deletequote(id=1)
        self.assertEqual(stampy.plugin.quote.getquote(), False)

    def test_quoteadd(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/quote add bacon tocino',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_quotelist(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/quote bacon',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_quotedel(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/quote del 1',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)
