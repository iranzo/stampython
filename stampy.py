#!/usr/bin/env python
# encoding: utf-8
#
# Description: Main module importer
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import logging
import stampy.stampy as stampy

if __name__ == "__main__":
    logger = logging.getLogger("stampy")
    logger.setLevel(logging.DEBUG)
    logger.debug(msg="Starting stampy wrapper")
    stampy.main()
