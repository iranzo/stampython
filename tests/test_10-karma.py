#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import stampy.plugin.karma
import cleanup


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
