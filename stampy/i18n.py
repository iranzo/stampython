#!/usr/bin/env python
# encoding: utf-8
#
# Description: Library for i18n translations
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import gettext
import os

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
translate = gettext.translation('stampy', localedir, fallback=True)
_ = translate.ugettext
