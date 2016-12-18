#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugins loader
# Author: Jack Waterworth (jack@redhat.com)
# Modifications: Pablo Iranzo Gómez (Pablo.Iranzo@gmail.com

import imp
import os
import logging

PluginFolder = "./stampy/plugin"
MainModule = "__init__"


def getPlugins():
    """
    Gets list of plugins in the plugins folder
    :return: list of plugins available
    """

    logger = logging.getLogger(__name__)
    plugins = []

    possibleplugins = os.listdir(PluginFolder)
    for i in possibleplugins:
        if i != "__init__.py" and os.path.splitext(i)[1] == ".py":
            i = os.path.splitext(i)[0]
        try:
            info = imp.find_module(i, [PluginFolder])
        except:
            info = False
        if i and info:
            logger.debug(msg="Plugging added: %s" % i)
            plugins.append({"name": i, "info": info})

    return plugins


def loadPlugin(plugin):
    """
    Loads selected plugin
    :param plugin: plugin to load
    :return: loader for plugin
    """
    return imp.load_module("stampy.stampy." + plugin["name"], *plugin["info"])
