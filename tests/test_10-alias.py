#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from stampy.stampy import getkarma, putkarma, createalias, getalias, deletealias


class TestStampy(TestCase):
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

    def test_removealias(self):
        deletealias('patata')
        self.assertEqual(getkarma('creilla'), 0)

    def test_removekarma(self):
        putkarma('patata', 0)
        self.assertEqual(getkarma('patata'), 0)
