#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import os

from zmon_worker_monitor.zmon_worker.errors import CheckError
from zmon_worker_monitor.adapters.ifunctionfactory_plugin import IFunctionFactoryPlugin, propartial

class OpenAMFactory(IFunctionFactoryPlugin):
    def __init__(self):
        super(OpenAMFactory, self).__init__()

    def configure(self, conf):
        """
        Called after plugin is loaded to pass the [configuration] section in their plugin info file
        :param conf: configuration dictionary
        """
        self.openam_base_url = conf.get('url')
        return

    def create(self, factory_ctx):
        """
        Automatically called to create the check function's object
        :param factory_ctx: (dict) names available for Function instantiation
        :return: an object that implements a check function
        """
        return propartial(OpenAMWrapper, url=self.openam_base_url)

class OpenAMError(CheckError):
    def __init__(self, message):
        self.message = message
        super(OpenAMError, self).__init__()

    def __str__(self):
        return 'OpenAM Error. Message: {}'.format(self.message)


class OpenAMWrapper(object):
    def __init__(
            self,
            url,
            params=None,
            timeout=10,
            max_retries=0,
            verify=True,
            headers=None,
            ):
        self.url = url
        self.params = params or {}
        self.headers = headers or {}

    def auth(self, chain=None, realm=None, user=os.getenv("OPENAM_USER"), password=os.getenv("OPENAM_PASSWORD")):
        if not user or user == "":
            raise OpenAMError("missing user")
        if not password or password == "":
            raise OpenAMError("missing password")
        if realm:
            self.params.update({"realm": realm})
        if chain:
            self.params.update({"service": chain})
            self.params.update({"authIndexType": "service"})
            self.params.update({"authIndexValue": chain})
        self.headers.update({"X-OpenAM-Username": user, "X-OpenAM-Password": password, "Content-Type": "application/json"})
        try:
            r = requests.post(self.url + "/json/authenticate", params=self.params, headers=self.headers, json={}, allow_redirects=False)
        except Exception, e:
            raise OpenAMError("failed to call OpenAM: "+str(e))

        try:
            data = r.json()
        except Exception, e:
            raise OpenAMError("failed to parse OpenAM json: "+str(e))

        result = {}
        result["success"] = 'tokenId' in data
        result["duration"] = r.elapsed.total_seconds()
        result["code"] = r.status_code
        return result

if __name__ == '__main__':
    import sys
    import logging
    from zmon_worker_monitor import plugin_manager

    logging.basicConfig(level=logging.INFO)

    # init plugin manager and collect plugins, as done by Zmon when worker is starting
    plugin_manager.init_plugin_manager()
    plugin_manager.collect_plugins(load_builtins=True, load_env=True)

    openam_url = sys.argv[1]
    factory_ctx = {}

    # eventlog = EventLogWrapper()
    openam = OpenAMWrapper(openam_url).auth(realm="/employees", chain="EmployeeChain")
    print(openam)
