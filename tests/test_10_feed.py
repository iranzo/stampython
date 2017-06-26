#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import stampy.plugin.feed


class TestStampy(TestCase):
    def test_addfeed(self):
        self.assertEqual(stampy.plugin.feed.feedadd(name='RHJobs', url='http://redhat.jobs/feed/rss', gid=0), 0)

    def test_listfeed(self):
        self.assertNotEqual(stampy.plugin.feed.listfeeds(), '')

    def test_testfeeds(self):
        stampy.plugin.feed.feeds()

    def test_delfeed(self):
        self.assertEqual(stampy.plugin.feed.feeddel(name='RHJobs', gid=0), True)

    def test_addfeedmessage(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/feed add '
                                                                u'RHJobs '
                                                                u'http://redhat.jobs/feed/rss',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_feedlist(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/feed list',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_feedtrigger(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/feed trigger',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_feeddel(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/feed del '
                                                                u'RHJobs',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)
