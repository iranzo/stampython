#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from stampy.stampy import config

from cleanup import clean


class TestStampy(TestCase):
    def test_owner(self):
        clean()
        self.assertEqual(config('owner'), 'iranzo')
