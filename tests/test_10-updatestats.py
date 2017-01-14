#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import cleanup
import stampy.stampy
import stampy.plugin.stats


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
