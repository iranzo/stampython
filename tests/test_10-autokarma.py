#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import stampy.plugin.autokarma


class TestStampy(TestCase):
    def test_createautok(self):
        self.assertEqual(stampy.plugin.autokarma.createautok('transcod', 'chupito'), True)

    def test_getautok(self):
        self.assertEqual(stampy.plugin.autokarma.getautok('transcod', 'chupito'), True)

    def test_removeautok(self):
        self.assertEqual(stampy.plugin.autokarma.deleteautok('transcod', 'chupito'), True)
