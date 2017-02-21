#!/usr/bin/env python
# encoding: utf-8

import logging
from unittest import TestCase

import cleanup
import stampy.plugin.forward
import stampy.stampy


logger = logging.getLogger(__name__)


class TestStampy(TestCase):
    cleanup.clean()

    def test_createfowrard(self):
        stampy.plugin.forward.createforward(source=1, target=2)
        for each in stampy.plugin.forward.getforward(source=1):
            self.assertEqual(each, u"2")
