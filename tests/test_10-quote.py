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
