#!/usr/bin/env python
# encoding: utf-8

import json
import math
import requests
import urllib

from collections import OrderedDict
from json import JSONDecodeError
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join
from requests.exceptions import RequestException
from time import sleep

from . import settings
from .exceptions import CoindeskAPIHttpRequestError

# Custom logger for client module
fileConfig(join(dirname(dirname(__file__)), 'logging.cfg'))
logger = getLogger(__name__)


class CoindeskAPIHttpRequest(object):
    """
    Enable Coindesk API http request.
    """

    def __init__(self, retries=10, allow_redirects=True):
        """
        Initialize Coindesk API http request making.

        :param int retries: number of request attempts before failing.
        :param bool allow_redirects: enable/disable http verbs redirection.
        """
        self._session = requests.Session()
        self._retries = retries
        self._allow_redirects = allow_redirects

    def __str__(self):
        """
        Represent class via params string.

        :return str: class representation.
        """
        classname = self.__class__.__name__
        return f'<{classname} - Coindesk api request>'

    @classmethod
    def start(cls, retries=10, allow_redirects=True):
        """
        Get Coindesk API http request instance.

        :param int retries: number of request attempts before failing.
        :param bool allow_redirects: enable/disable http verbs redirection.
        :return cls: CoindeskAPICient class instance.
        """
        retries, allow_redirects = cls.validate(retries, allow_redirects)
        return cls(retries, allow_redirects)

    @staticmethod
    def validate(retries, allow_redirects):
        """
        Validate initialization parameters.

        :param int retries: number of request attempts before failing.
        :param bool allow_redirects: enable/disable http verbs redirection.
        :return tuple: validated params.
        """
        # TODO:
        # retries = utils.validate_retries(retries)
        # allow_redirects = utils.validate_redirects(allow_redirects)
        return retries, allow_redirects

    @property
    def retries(self):
        """
        Get number of request attempts.

        :return int: number of request attempts before failing.
        """
        return self._retries

    @retries.setter
    def retries(self, retries):
        """
        Set number of request attempts.

        :param int retries: number of request attempts before failing.
        """
        # TODO:
        # retries = utils.validate_retries(retries)
        self._retries = retries

    @property
    def redirects(self):
        """
        Check if redirects are allowed.

        :return bool: http verbs redirection status.
        """
        return self._allow_redirects

    @redirects.setter
    def redirects(self, redirects):
        """
        Set/unset redirects.

        :param bool redirects: enable/disable http verbs redirection.
        """
        # TODO:
        # redirects = utils.validate_redirects(redirects)
        self._allow_redirects = redirects

    def get(self, url, params={}, raw=False):
        """
        Retrieve response object/data from Coindesk API url.

        :param str url: api resource locator.
        :param dict params: optional query parameters.
        :param bool raw: enable/disable api response parsing.
        :return *: api http raw response or response data.
        """
        data = None
        response = self._http_request(url, params)
        status_code = response.status_code

        if status_code == requests.codes.not_found:
            msg = f'Status {status_code}.'
            logger.error(f'[CoindeskAPIHttpRequest] Request error. {msg}')
            raise CoindeskAPIHttpRequestError(msg)
        if status_code == requests.codes.forbidden:
            msg = f'Status {status_code}.'
            logger.error(f'[CoindeskAPIHttpRequest] Request error. {msg}')
            raise CoindeskAPIHttpRequestError(msg)

        if raw:
            data = response
            msg = f'Status {status_code}. Raw response.'
            logger.info(f'[CoindeskAPIHttpRequest] Request success. {msg}')
        if response.text:
            try:
                data = response.json()
            except JSONDecodeError as err:
                msg = f'Could not decode json data. {err.args[0]}.'
                logger.error(f'[CoindeskAPIHttpRequest] Request error. {msg}')
                raise CoindeskAPIHttpRequestError(msg)
            msg = f'status {status_code}. JSON response.'
            logger.info(f'[CoindeskAPIHttpRequest] Request success. {msg}')
        return data

    def _http_request(self, url, params):
        """
        Make http request to Coindesk API.

        :param str url: api resource locator.
        :param dict params: optional query parameters.
        :return obj: http response object.
        """
        url = self._get_url_with_params(url, params)
        options = self._get_request_options()

        for retry in range(1, self.retries + 1):
            try:
                with self._session as request:
                    response = request.get(url=url, **options)
            except RequestException as err:
                timeout = math.pow(2, retry)
                logger.error(f'[CoindeskAPIHttpRequest] Retry {retry} request. {err.args[0]}.')
                logger.error(f'[CoindeskAPIHttpRequest] Waiting {timeout} ms.')
                sleep(timeout)
            else:
                msg = f'Status {response.status_code}. Coindesk API url {response.url}.'
                logger.info(f'[CoindeskAPIHttpRequest] Request success. {msg}')
                return response
        else:
            msg = f'No response from Coindesk API url {url}.'
            logger.error(f'[CoindeskAPIHttpRequest] Request error. {msg}')
            raise CoindeskAPIHttpRequestError(msg)

    def _get_url_with_params(self, url, params):
        """
        Add params to base url.

        :param str url: api resource locator.
        :param dict params: optional query parameters.
        :return str: api resource locator with optional params.
        """
        if params:
            params = urllib.parse.urlencode(params)
            url = f'{url}?{params}'
        return urllib.parse.quote(url, '=/?:&')

    def _get_request_options(self):
        """
        Return http get request option parameters.
        """
        return {
            'headers': OrderedDict(settings.REQUEST_HEADERS),
            'allow_redirects': self.redirects,
            'timeout': settings.REQUEST_TIMEOUT
        }
