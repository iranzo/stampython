#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import cleanup
import stampy.plugin.karma


class TestStampy(TestCase):
    cleanup.clean()

    def test_putkarma(self):
        stampy.plugin.karma.putkarma('patata', 0)
        self.assertEqual(stampy.plugin.karma.getkarma('patata'), 0)

    def test_updatekarmaplus(self):
        stampy.plugin.karma.updatekarma('patata', 2)
        self.assertEqual(stampy.plugin.karma.getkarma('patata'), 2)

    def test_updatekarmarem(self):
        stampy.plugin.karma.updatekarma('patata', -1)
        self.assertEqual(stampy.plugin.karma.getkarma('patata'), 1)

    def test_rank(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'rank',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_skarma(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'skarma cebolla=20',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_srank(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'srank iranzo',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_skarmapurge(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'skarma purge',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)
