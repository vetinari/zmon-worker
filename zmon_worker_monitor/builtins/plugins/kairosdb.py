#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
import sys
import os

import tokens

from zmon_worker_monitor.zmon_worker.errors import HttpError, ConfigurationError

from zmon_worker_monitor.zmon_worker.common.http import init_tokens

from zmon_worker_monitor.adapters.ifunctionfactory_plugin import IFunctionFactoryPlugin, propartial

logger = logging.getLogger('zmon-worker.kairosdb-function')


DATAPOINTS_ENDPOINT = 'api/v1/datapoints/query'


class KairosdbFactory(IFunctionFactoryPlugin):
    def __init__(self):
        super(KairosdbFactory, self).__init__()
        self._url = None

    def configure(self, conf):
        """
        Called after plugin is loaded to pass the [configuration] section in their plugin info file
        :param conf: configuration dictionary
        """
        self._url = conf.get('url')
        init_tokens(conf)

    def create(self, factory_ctx):
        """
        Automatically called to create the check function's object
        :param factory_ctx: (dict) names available for Function instantiation
        :return: an object that implements a check function
        """
        return propartial(KairosdbWrapper, url=self._url)


class KairosdbWrapper(object):
    def __init__(self, url, oauth2=False, oauth2_token_name='uid'):
        if not url:
            raise ConfigurationError('KairosDB wrapper improperly configured. URL is missing!')

        self.url = url

        self.__session = requests.Session()

        if oauth2:
            self.__session.headers.update({'Authorization': 'Bearer {}'.format(tokens.get(oauth2_token_name))})

    def query(self, name, group_by=None, tags=None, start=5, end=0, time_unit='minutes', aggregators=None,
              start_absolute=None, end_absolute=None):
        """
        Query kairosdb.

        :param name: Metric name.
        :type name: str

        :param group_by: List of fields to group by.
        :type group_by: list

        :param tags: Filtering tags.
        :type tags: dict

        :param start: Relative start time. Default is 5.
        :type start: int

        :param end: End time. Default is 0.
        :type end: int

        :param time_unit: Time unit ('seconds', 'minutes', 'hours'). Default is 'minutes'.
        :type time_unit: str.

        :param aggregators: List of aggregators.
        :type aggregators: list

        :param start_absolute: Absolute start time in milliseconds, overrides the start parameter which is relative
        :type start_absolute: long

        :param end_absolute: Absolute end time in milliseconds, overrides the end parameter which is relative
        :type end_absolute: long

        :return: Result queries.
        :rtype: dict
        """
        url = os.path.join(self.url, DATAPOINTS_ENDPOINT)

        if start < 1 or end < 0:
            raise ValueError('Time relative "start" and "end" must be greater than or equal to 1')

        if group_by is None:
            group_by = []

        q = {'metrics': [{
            'name': name,
            'group_by': group_by
        }]}

        if start_absolute is None:
            q['start_relative'] = {
                'value': start,
                'unit': time_unit
            }
        else:
            q['start_absolute'] = start_absolute

        if end_absolute is None:
            if end > 0:
                q['end_relative'] = {
                    'value': end,
                    'unit': time_unit
                }
        else:
            q['end_absolute'] = end_absolute

        if aggregators:
            q['metrics'][0]['aggregators'] = aggregators

        if tags:
            q['metrics'][0]['tags'] = tags

        try:
            response = self.__session.post(url, json=q)
            if response.ok:
                return response.json()['queries'][0]
            else:
                raise Exception(
                    'KairosDB Query failed: {} with status {}:{}'.format(q, response.status_code, response.text))
        except requests.Timeout:
            raise HttpError('timeout', self.url), None, sys.exc_info()[2]
        except requests.ConnectionError:
            raise HttpError('connection failed', self.url), None, sys.exc_info()[2]

    def tagnames(self):
        return []

    def metric_tags(self):
        return {}
