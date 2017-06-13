#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import cleanup
import stampy.plugin.config


class TestStampy(TestCase):
    def test_owner(self):
        cleanup.clean()
        self.assertEqual(stampy.plugin.config.config('owner'), 'iranzo')
