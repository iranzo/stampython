#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from stampy.stampy import getkarma, updatekarma, putkarma, config, setconfig,\
    sendmessage, createdb

# Precreate DB for other operations to work
try:
    createdb()
except:
    pass

# Define configuration for tests
setconfig('token', '279488169:AAFqGVesZ-83n9sFxfLQxUUCVO8_8L3JNEU')
setconfig('owner', 'iranzo')
setconfig('url', 'https://api.telegram.org/bot')


class TestStampy(TestCase):
    def test_owner(self):
        self.assertEqual(config('owner'), 'iranzo')

    def test_putkarma(self):
        putkarma('patata', 0)
        self.assertEqual(getkarma('patata'), 0)

    def test_getkarma(self):
        self.assertEqual(getkarma('patata'), 0)

    def test_updatekarmaplus(self):
        updatekarma('patata', 1)
        self.assertEqual(getkarma('patata'), 1)

    def test_updatekarmarem(self):
        updatekarma('patata', -1)
        self.assertEqual(getkarma('patata'), 0)

    def test_removekarma(self):
        putkarma('patata', 0)
        self.assertEqual(getkarma('patata'), 0)

    def test_sendmessage(self):
        sendmessage(chat_id="-158164217", text="UT test")
