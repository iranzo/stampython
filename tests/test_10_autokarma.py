#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import cleanup
import stampy.plugin.autokarma


class TestStampy(TestCase):
    cleanup.clean()

    def test_createautok(self):
        self.assertEqual(stampy.plugin.autokarma.createautok('transcod', 'chupito'), True)

    def test_getautok(self):
        self.assertEqual(stampy.plugin.autokarma.getautok('transcod'), ['chupito'])

    def test_removeautok(self):
        self.assertEqual(stampy.plugin.autokarma.deleteautok('transcod', 'chupito'), True)

    def test_autoklist(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/autok list',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_autokadd(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/autok bacon=tocino',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_autokdel(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/autok delete bacon=tocino',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_autokwords(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'bacon transcod',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)
