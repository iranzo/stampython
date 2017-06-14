#!/usr/bin/env python
# encoding: utf-8

import logging
from unittest import TestCase

import cleanup
import stampy.plugin.alias
import stampy.plugin.karma
import stampy.stampy

logger = logging.getLogger(__name__)


class TestStampy(TestCase):
    cleanup.clean()

    def test_createalias(self):
        stampy.plugin.alias.createalias('patata', 'creilla')
        self.assertEqual(stampy.plugin.alias.getalias('patata'), 'creilla')

    def test_getalias(self):
        self.assertEqual(stampy.plugin.alias.getalias('patata'), 'creilla')

    def test_increasealiaskarma(self):
        cleanup.clean()

        stampy.plugin.karma.putkarma('patata', 1)
        self.assertEqual(stampy.plugin.karma.getkarma('patata'), 1)

        # Alias doesn't get increased as the 'aliases' modifications are in
        # process, not in the individual functions
        self.assertEqual(stampy.plugin.karma.getkarma('creilla'), 0)

        # Reset patata status for the next test
        stampy.plugin.karma.putkarma('patata', 0)

        # Create alias
        stampy.plugin.alias.createalias(word='patata', value='creilla')

        # Process alias instead via process()
        text = [{u'message': {u'date': 1478361249, u'text': u'patata++', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 108, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253571}]
        stampy.stampy.process(text)

        # Karma has been given to patata, but alias gave it to creilla
        self.assertEqual(stampy.plugin.karma.getkarma('patata'), 0)
        self.assertEqual(stampy.plugin.karma.getkarma('creilla'), 1)

    def test_increasealiaskarmawithcombine(self):
        cleanup.clean()

        # Process alias instead via process()
        text = [{u'message': {u'date': 1478361249, u'text': u'patata++', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 108, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253571}]
        stampy.stampy.process(text)

        self.assertEqual(stampy.plugin.karma.getkarma('patata'), 1)

        stampy.plugin.alias.createalias('patata', 'creilla')

        # Process alias instead via process()
        text = [{u'message': {u'date': 1478361249, u'text': u'patata++', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 108, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253571}]
        stampy.stampy.process(text)

        # Karma has been given to patata, but alias gave it to creilla and also it was combined with previous karma
        self.assertEqual(stampy.plugin.karma.getkarma('patata'), 0)
        self.assertEqual(stampy.plugin.karma.getkarma('creilla'), 2)

    def test_removealias(self):
        stampy.plugin.alias.deletealias('patata')

        # After alias has been removed, the words are no longer linked
        self.assertEqual(stampy.plugin.karma.getkarma('creilla'), 2)
        self.assertEqual(stampy.plugin.karma.getkarma('patata'), 0)

        # Increase  karma again via process and revalidate
        text = [{u'message': {u'date': 1478361249, u'text': u'patata++', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 108, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253571}]
        stampy.stampy.process(text)

        self.assertEqual(stampy.plugin.karma.getkarma('creilla'), 2)
        self.assertEqual(stampy.plugin.karma.getkarma('patata'), 1)

    def test_aliaslist(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/alias list',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_aliasadd(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/alias bacon=tocino',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)

    def test_aliasdel(self):
        messages = [{u'message': {u'date': 1478361249, u'text': u'/alias delete bacon',
                                  u'from': {u'username': u'iranzo',
                                            u'first_name': u'Pablo',
                                            u'last_name': u'Iranzo G\xf3mez',
                                            u'id': 5812695}, u'message_id': 108,
                                  u'chat': {u'all_members_are_administrators': True,
                                            u'type': u'group', u'id': -158164217,
                                            u'title': u'BOTdevel'}},
                     u'update_id': 837253571}]
        stampy.stampy.process(messages)
