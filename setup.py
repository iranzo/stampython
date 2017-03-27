#!/usr/bin/env python
# encoding: utf-8

from distutils.core import setup
from babel.messages import frontend as babel

setup(
    name='stampython',
    version='0.50',
    packages=['stampy'],
    url='https://github.com/iranzo/stampython',
    license='GPL',
    author='Pablo Iranzo Gómez',
    author_email='Pablo.Iranzo@gmail.com',
    description='Telegram bot for controlling Karma',
    cmdclass={'compile_catalog': babel.compile_catalog,
              'extract_messages': babel.extract_messages,
              'init_catalog': babel.init_catalog,
              'update_catalog': babel.update_catalog},
)
