#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import cleanup
import stampy.plugin.stats
import stampy.stampy


class TestStampy(TestCase):
    cleanup.clean()

    def test_00stats(self):
        # test that no empty [] groups are added
        stampy.plugin.stats.updatestats(type='chat', id=-1, name="Test",
                                        date=False, memberid=[])
        self.assertEqual(stampy.plugin.stats.getstats(id=-1, type='chat'),
                         ('chat', -1, u"Test", u'False', 1, []))

    def test_01pingchat(self):
        stampy.plugin.stats.pingchat(-1)
        (type, id, name, date, count, memberid) = stampy.plugin.stats.getstats(
            type='chat', id=-1)
        self.assertEqual(stampy.plugin.stats.getstats(id=-1, type='chat'),
                         ('chat', -1, u"Test", date, count, []))

    def test_02statsshow(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/stats show',
                              u'from': {u'username': u'iranzo',
                                        u'first_name': u'Pablo',
                                        u'last_name': u'Iranzo G\xf3mez',
                                        u'id': 5812695}, u'message_id': 108,
                              u'chat': {u'all_members_are_administrators': True,
                                        u'type': u'group', u'id': -158164217,
                                        u'title': u'BOTdevel'}},
                 u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_02statssearch(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/stats search',
                              u'from': {u'username': u'iranzo',
                                        u'first_name': u'Pablo',
                                        u'last_name': u'Iranzo G\xf3mez',
                                        u'id': 5812695}, u'message_id': 108,
                              u'chat': {u'all_members_are_administrators': True,
                                        u'type': u'group', u'id': -158164217,
                                        u'title': u'BOTdevel'}},
                 u'update_id': 837253571}]
        stampy.stampy.process(messages)


    def test_dochatcleanup(self):
        stampy.plugin.stats.dochatcleanup()
