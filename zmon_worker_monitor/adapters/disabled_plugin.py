#!/usr/bin/env python
# -*- coding: utf-8 -*-


class DisabledPlugin(object):
    _plugin_name = 'unknown'

    def __init__(self, name):
        """
        Set the basic variables.
        """
        self.is_activated = False
        self._plugin_name = name

    def activate(self):
        """
        Called at plugin activation.
        """
        pass

    def deactivate(self):
        """
        Called when the plugin is disabled.
        """
        self.is_activated = False

    def configure(self, conf):
        pass

    def __getattr__(self, name):
        raise Exception('plugin {} is disabled, called: {}'.format(self._plugin_name, name))
