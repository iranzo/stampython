#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from stampy.stampy import getquote, addquote, deletequote


class TestStampy(TestCase):
    def test_addquote(self):
        self.assertEqual(addquote('iranzo', 'now', 'Test'), 1)

    def test_getquote(self):
        self.assertEqual(getquote(),
                         (1, 'iranzo', 'now', 'Test'))

    def test_removequote(self):
        deletequote(id=1)
        self.assertEqual(getquote(), False)
