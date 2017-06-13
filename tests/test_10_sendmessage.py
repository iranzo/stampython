#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import stampy.stampy


class TestStampy(TestCase):
    def test_sendmessage(self):
        stampy.stampy.sendmessage(chat_id="-158164217", text="UT test")
