#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from stampy.stampy import getkarma, putkarma, createalias, getalias, deletealias, process
from cleanup import clean


class TestStampy(TestCase):
    clean()

    def test_createalias(self):
        createalias('patata', 'creilla')
        self.assertEqual(getalias('patata'), 'creilla')

    def test_getalias(self):
        self.assertEqual(getalias('patata'), 'creilla')

    def test_increasealiaskarma(self):
        putkarma('patata', 1)
        self.assertEqual(getkarma('patata'), 1)

        # Alias doesn't get increased as the 'aliases' modifications are in
        # process, not in the individual functions
        self.assertEqual(getkarma('creilla'), 0)

        # Reset patata status for the next test
        putkarma('patata', 0)

        # Process alias instead via process()
        text = [{u'message': {u'date': 1478361249, u'text': u'patata++', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 108, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253571}]
        process(text)

        # Karma has been given to patata, but alias gave it to creilla
        self.assertEqual(getkarma('creilla'), 1)

    def test_increasealiaskarmawithcombine(self):
        clean()

        # Process alias instead via process()
        text = [{u'message': {u'date': 1478361249, u'text': u'patata++', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 108, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253571}]
        process(text)

        self.assertEqual(getkarma('patata'), 1)

        createalias('patata', 'creilla')

        # Process alias instead via process()
        text = [{u'message': {u'date': 1478361249, u'text': u'patata++', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 108, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253571}]
        process(text)

        # Karma has been given to patata, but alias gave it to creilla and also it was combined with previous karma
        self.assertEqual(getkarma('patata'), 0)
        self.assertEqual(getkarma('creilla'), 2)

    def test_removealias(self):
        deletealias('patata')

        # After alias has been removed, the words are no longer linked
        self.assertEqual(getkarma('creilla'), 2)
        self.assertEqual(getkarma('patata'), 0)

        # Increase  karma again via process and revalidate
        text = [{u'message': {u'date': 1478361249, u'text': u'patata++', u'from': {u'username': u'iranzo', u'first_name': u'Pablo', u'last_name': u'Iranzo G\xf3mez', u'id': 5812695}, u'message_id': 108, u'chat': {u'all_members_are_administrators': True, u'type': u'group', u'id': -158164217, u'title': u'BOTdevel'}}, u'update_id': 837253571}]
        process(text)

        self.assertEqual(getkarma('creilla'), 2)
        self.assertEqual(getkarma('patata'), 1)
