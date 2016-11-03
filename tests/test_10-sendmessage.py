#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from stampy.stampy import sendmessage


class TestStampy(TestCase):
    def test_sendmessage(self):
        sendmessage(chat_id="-158164217", text="UT test")
