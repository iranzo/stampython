#!/usr/bin/env python
# encoding: utf-8
#
# Description: Library for i18n translations
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import gettext
import logging
import os

import stampy


def _(string):
    """
    Provides translation of string based on current language
    :param string: String to translate
    :return: Translated string
    """
    language = stampy.language

    localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    trad = gettext.translation('stampy', localedir, fallback=True, languages=[language])
    return trad.ugettext(string)


def _L(string):
    """
    Provides translation of string based on current language
    :param string: String to translate
    :return: Translated string
    """
    loglanguage = stampy.loglanguage

    localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    trad = gettext.translation('stampy', localedir, fallback=True, languages=[loglanguage])
    return trad.ugettext(string)


def chlang(lang=False):
    """
    Changes default language
    :param lang: Language to change to
    """
    logger = logging.getLogger(__name__)
    if lang:
        stampy.language = lang
        logger.debug(msg=_L("Language changed to %s") % lang)
