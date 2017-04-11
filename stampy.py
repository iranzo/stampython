#!/usr/bin/env python
# encoding: utf-8
#
# Description: Main module importer
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging
import stampy.stampy as stampy

if __name__ == "__main__":
    __name__ = "stampy"
    logger = logging.getLogger(__name__)
    stampy.main()
