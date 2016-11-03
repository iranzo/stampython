#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from stampy.stampy import createautok, getautok, deleteautok


class TestStampy(TestCase):
    def test_createautok(self):
        self.assertEqual(createautok('transcod', 'chupito'), True)

    def test_getautok(self):
        self.assertEqual(getautok('transcod', 'chupito'), True)

    def test_removeautok(self):
        self.assertEqual(deleteautok('transcod', 'chupito'), True)
