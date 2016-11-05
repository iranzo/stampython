#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from stampy.stampy import process

true = True

# Obtained from bot URL after sending some sample text, can be used to
# perform tests in a different way:
#
# Instead of performing individual tests of functions like we do on the others
# we can do testing the whole bot code as a block, adding karma, creating
# aliases, validating that they get the proper karma added, etc
#
#
# validation should be performed after process(text) with the individual
# expected results (karma of word 'xxx' === 'yyy', aliases defined, updated
# stats, etc)

text = [{u'message': {u'date': 1478361249, u'text': u'word++', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 108, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253571}, {u'message': {u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'text': u'/alias word=palabra', u'entities': [{u'length': 6, u'type': u'bot_command', u'offset': 0}], u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}, u'date': 1478361255, u'message_id': 109}, u'update_id': 837253572}, {u'message': {u'date': 1478361259, u'text': u'word++', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 110, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253573}, {u'message': {u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'text': u'/help', u'entities': [{u'length': 5, u'type': u'bot_command', u'offset': 0}], u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}, u'date': 1478361268, u'message_id': 111}, u'update_id': 837253574}, {u'message': {u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'text': u'/alias delete word', u'entities': [{u'length': 6, u'type': u'bot_command', u'offset': 0}], u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}, u'date': 1478361297, u'message_id': 112}, u'update_id': 837253575}, {u'message': {u'date': 1478361299, u'text': u'rank word', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 113, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253576}, {u'message': {u'date': 1478361300, u'text': u'rank patata', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 114, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253577}, {u'message': {u'date': 1478361304, u'text': u'word--', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 115, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253578}]


class TestStampy(TestCase):
    def test_process(self):
        text = ""
        process(text)
