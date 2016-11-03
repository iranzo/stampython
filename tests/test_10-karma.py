#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from stampy.stampy import getkarma, updatekarma, putkarma


class TestStampy(TestCase):
    def test_putkarma(self):
        putkarma('patata', 0)
        self.assertEqual(getkarma('patata'), 0)

    def test_getkarma(self):
        self.assertEqual(getkarma('patata'), 0)

    def test_updatekarmaplus(self):
        updatekarma('patata', 2)
        self.assertEqual(getkarma('patata'), 2)

    def test_updatekarmarem(self):
        updatekarma('patata', -1)
        self.assertEqual(getkarma('patata'), 1)
