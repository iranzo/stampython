#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugins loader
# Author: Jack Waterworth (jack@redhat.com)
# Modifications: Pablo Iranzo Gómez (Pablo.Iranzo@gmail.com

import imp
import logging
import os

import plugin.config
from i18n import _L

PluginFolder = "./stampy/plugin"


def getPlugins():
    """
    Gets list of plugins in the plugins folder
    :return: list of plugins available
    """

    __name__ = 'stampy.stampy.plugins'
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
            if i not in plugin.config.config(key='disabled_plugins',
                                             default=''):
                logger.debug(msg=_L("Plugin added: %s") % i)
                plugins.append({"name": i, "info": info})
            else:
                logger.debug(msg=_L("Plugin disabled: %s") % i)

    return plugins


def loadPlugin(plugin):
    """
    Loads selected plugin
    :param plugin: plugin to load
    :return: loader for plugin
    """
    return imp.load_module("stampy.stampy." + plugin["name"], *plugin["info"])


def initplugins():
    """
    Initializes plugins
    :return: list of plugin modules initialized
    """

    __name__ = 'stampy.stampy.plugins'
    logger = logging.getLogger(__name__)

    plugs = []
    plugtriggers = {}
    for i in getPlugins():
        logger.debug(msg=_L("Processing plugin initialization: %s") % i["name"])
        newplug = loadPlugin(i)
        plugs.append(newplug)
        triggers = list(newplug.init())
        plugtriggers[i["name"]] = triggers
        logger.debug(msg=_L("Plugin %s is triggered by %s") % (i["name"], triggers))
    return plugs, plugtriggers
