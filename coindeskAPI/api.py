#!/usr/bin/env python
# encoding: utf-8

import configparser
import json
import os
import requests

from .exceptions import (CoinDeskAPIError,
                        CoinDeskAPIHttpRequestError,
                        CoinDeskAPIHttpResponseError)


class CoinDeskAPI(object):
    """
    Enable CoinDesk API use.
    """

    def __init__(self, data, url):
        """
        Initialize CoinDesk API.

        :param str url: CoinDesk API url to request to.
        """
        self._api_data = data
        self._api_url = url

    def __str__(self):
        """
        Represent class via params string.

        :return str: class representarion.
        """
        params = {
            'classname': self.__class__.__name__,
            'data': self._api_data,
            'url': self._api_url,
        }
        return '<{classname}:\ndata: {data}\nurl: {url}>'.format(**params)

    @classmethod
    def config(cls, data=None, filename='coindesk.cfg', section='api'):
        """
        Get CoinDesk API's base url.

        :param str data: type of data to fetch (currentprice, historical).
        :param str filename: CoinDesk API configuration filename.
        :param str section: filename section to parse.
        :return cls: CoinDeskAPI class instance.
        """
        parser = configparser.ConfigParser()
        parser.read(filename)
        if parser.has_section(section):
            base_url = parser.get(section, 'base_url')
            data_url = parser.get(section, data)
        else:
            msg = 'Section {} not found in {} file'.format(section, filename)
            raise CoinDeskAPIError(msg)

        api_url = base_url + data_url
        return cls(data, api_url)

    def call(self, **kwargs):
        """
        Make http request to CoinDesk API.

        :param str method: CoinDesk API request method.
        :param str url: API url to request to.
        :return json: request result.
        """
        response = CoinDeskHttpRequestAPI.get(self._api_url, **kwargs)
        json_result = CoinDeskHttpResponseAPI.parse(response)
        return json_result


class CoinDeskHttpRequestAPI(object):
    """
    Enable CoinDesk API data request.
    """
    pass


class CoinDeskHttpResponseAPI(object):
    """
    Enable CoinDEsk API response data parsing.
    """
    pass
