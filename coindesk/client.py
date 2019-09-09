#!/usr/bin/env python
# encoding: utf-8

import json
import jsonschema
import math
import requests
import urllib

from collections import OrderedDict
from json import JSONDecodeError
from jsonschema import SchemaError, ValidationError
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join
from requests.exceptions import RequestException
from time import sleep

from . import settings, utils
from .exceptions import (CoindeskAPIClientError,
                         CoindeskAPIHttpRequestError,
                         CoindeskAPIHttpResponseError)

# Custom logger for client module
fileConfig(join(dirname(dirname(__file__)), 'logging.cfg'))
logger = getLogger(__name__)


class CoindeskAPIHttpRequest(object):
    """
    Enable Coindesk API http request.
    """

    def __init__(self, retries=10, redirects=True, timeout=5, backoff=True):
        """
        Initialize Coindesk API http request making.

        :param int retries: number of request attempts before failing.
        :param bool redirects: enable/disable http verbs redirection.
        :param int timeout: seconds before request timeout.
        :param bool backoff: enable/disable http request retry backoff.
        """
        self._session = requests.Session()
        self._retries = retries
        self._redirects = redirects
        self._timeout = timeout
        self._backoff = backoff

    def __str__(self):
        """
        Represent class via params string.

        :return str: class representation.
        """
        classname = self.__class__.__name__
        return f'<{classname} - Coindesk api request>'

    @classmethod
    def start(cls, retries=10, redirects=True, timeout=5, backoff=True):
        """
        Get Coindesk API http request instance.

        :param int retries: number of request attempts before failing.
        :param bool redirects: enable/disable http verbs redirection.
        :param int timeout: seconds before request timeout.
        :param bool backoff: enable/disable http request retry backoff.
        :return cls: CoindeskAPICient class instance.
        """
        retries, redirects, timeout, backoff = cls.validate(retries, redirects, timeout, backoff)
        return cls(retries, redirects, timeout, backoff)

    @staticmethod
    def validate(retries, redirects, timeout, backoff):
        """
        Validate initialization parameters.

        :param int retries: number of request attempts before failing.
        :param bool redirects: enable/disable http verbs redirection.
        :param int timeout: seconds before request timeout.
        :param bool backoff: enable/disable http request retry backoff.
        :return tuple: validated params.
        """
        retries = utils.validate_retries(retries)
        redirects = utils.validate_redirects(redirects)
        timeout = utils.validate_timeout(timeout)
        backoff = utils.validate_backoff(backoff)
        return retries, redirects, timeout, backoff

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
        retries = utils.validate_retries(retries)
        self._retries = retries

    @property
    def redirects(self):
        """
        Check if requests redirects are allowed.

        :return bool: http verbs redirection status.
        """
        return self._redirects

    @redirects.setter
    def redirects(self, redirects):
        """
        Set/unset redirects.

        :param bool redirects: enable/disable http verbs redirection.
        """
        redirects = utils.validate_redirects(redirects)
        self._redirects = redirects

    @property
    def timeout(self):
        """
        Get number of seconds for request timeout.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        """
        Set number of seconds for request timeout.

        :param int timeout: seconds before request timeout.
        """
        timeout = utils.validate_timeout(timeout)
        self._timeout = timeout

    @property
    def backoff(self):
        """
        Check if requests retries backoff is enabled.

        :return bool: request retries backoff status.
        """
        return self._backoff

    @backoff.setter
    def backoff(self, backoff):
        """
        Set/unset request backoff.

        :param bool backoff: enable/disable http requests backoff.
        """
        backoff = utils.validate_backoff(backoff)
        self._backoff = backoff

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
        elif response.text:
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
                timeout = math.pow(2, retry) if self.backoff else 0
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
            'timeout': self.timeout
        }


class CoindeskAPIClient(CoindeskAPIHttpRequest):
    """
    Enable Coindesk API use.
    """

    def __init__(self, data_type=None, params={}, retries=10, redirects=True, timeout=5, backoff=True):
        """
        Initialize Coindesk API client.

        :param str data_type: type of data to fetch (currentprice, historical).
        :param dict params: optional url query parameters.
        :param int retries: number of request attempts before failing.
        :param bool redirects: enable/disable http verbs redirection.
        :param int timeout: seconds before request timeout.
        :param bool backoff: enable/disable http request retry backoff.
        """
        super(CoindeskAPIClient, self).__init__(retries, redirects, timeout, backoff)
        self._data_type = data_type
        self._params = params
        self._api_path = self._get_api_path()
        self._api_endpoint = self._construct_api_endpoint(data_type, params)

    def __str__(self):
        """
        Represent class via params string.

        :return str: class representation.
        """
        classname = self.__class__.__name__
        endpoint = self._api_endpoint
        return f'<{classname}:\nendpoint: {endpoint}>'

    @classmethod
    def start(cls, data_type=None, params={}, retries=10, redirects=True, timeout=5, backoff=True):
        """
        Get Coindesk API client instance.

        :param str data_type: type of data to fetch (currentprice, historical).
        :param dict params: optional url query parameters.
        :param int retries: number of request attempts before failing.
        :param bool redirects: enable/disable http verbs redirection.
        :param int timeout: seconds before request timeout.
        :param bool backoff: enable/disable http request retry backoff.
        :return cls: CoindeskAPICient class instance.
        """
        data_type = utils.validate_data_type(data_type)
        params = utils.validate_params(data_type, params)
        retries, redirects, timeout, backoff = cls.validate(retries, redirects, timeout, backoff)
        return cls(data_type, params, retries, redirects, timeout, backoff)

    def _get_api_path(self):
        """
        Get Coindesk api base url.

        :return str: Coindesk api base url.
        """
        protocol, host, path = settings.API_PROTOCOL, settings.API_HOST, settings.API_PATH
        api_path = f'{protocol}://{host}{path}'
        return self._clean_api_path(api_path)

    def _clean_api_path(self, api_path):
        """
        Clean Coindesk api base url.

        :param str api_path: Coindesk api base url.
        :return str: cleaned Coindesk api base url.
        """
        return f'{api_path}/' if not api_path.endswith('/') else api_path

    def _construct_api_endpoint(self, data_type, params):
        """
        Get Coindesk api endpoint.

        :param str data_type: type of data to fetch (currentprice, historical).
        :param dict params: optional query parameters.
        :return str: Coindesk api endpoint for correspondig data resource.
        """
        resource = settings.API_ENDPOINTS.get(data_type)
        if data_type == settings.API_CURRENTPRICE_DATA_TYPE:
            currency_param = params.pop(settings.CURRENCY_PARAM, '')
            currency = f'/{currency_param}' if currency_param else currency_param
            resource = resource.format(currency=currency)
        return f'{self._api_path}{resource}'

    @property
    def data_type(self):
        """
        Get Coindesk data type resource.
        """
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        """
        Set Coindesk API client data type and corresponding api path attribute.

        :param str value: type of data to fetch (currentprice, historical).
        """
        self._data_type = utils.validate_data_type(data_type)
        if data_type == settings.API_CURRENTPRICE_DATA_TYPE:
            self._params = {}
        self._api_endpoint = self._construct_api_endpoint(data_type, self._params)

    @property
    def params(self):
        """
        Get Coindesk api endpoint optional query parameters.
        """
        return self._params

    @params.setter
    def params(self, params):
        """
        Set Coindesk API client optinal query parameters.

        :param dict payload: optional url query parameters.
        """
        self._params = utils.validate_params(self._data_type, params)
        self._api_endpoint = self._construct_api_endpoint(self._data_type, params)

    @property
    def url(self):
        """
        Get Coindesk api endpoint.
        """
        return self._api_endpoint

    @property
    def valid_params(self):
        """
        Get Coindesk valid query parameters for api endpoint.
        """
        if self._data_type == settings.API_CURRENTPRICE_DATA_TYPE:
            return settings.VALID_CURRENTPRICE_PARAMS
        elif self._data_type == settings.API_HISTORICAL_DATA_TYPE:
            return settings.VALID_HISTORICAL_PARAMS
        else:
            msg = f'Uncorrect data type setup for {self._data_type}.'
            logger.warning(f'[CoindeskAPICient] Data type error. {msg}')
            return None

    def get_supported_currencies(self):
        """
        Get Coindesk valid currencies list.
        """
        protocol, host, path = settings.API_PROTOCOL, settings.API_HOST, settings.API_PATH
        resource = settings.API_ENDPOINTS.get(settings.API_SUPPORTED_CURRENCIES_DATA_TYPE)
        url = f'{protocol}://{host}{path}/{resource}'
        try:
            currencies = super(CoindeskAPIClient, self).get(url, {}, False)
        except Exception as err:
            msg = err.args[0]
            logger.warning(f'[CoindeskAPICient] Get currencies error. {msg}')

        print(currencies)
        if currencies: utils.validate_currencies_settings(currencies)
        return currencies if currencies else utils.get_currencies_settings()

    def get(self, raw=False):
        """
        Make http request to Coindesk API.

        :param bool raw: enable/disable api response parsing.
        :return *: api http raw response or data.
        """
        try:
            return super(CoindeskAPIClient, self).get(self.url, self.params, raw)
        except Exception as err:
            msg = err.args[0]
            logger.error(f'[CoindeskAPICient] API call error. {msg}.')
            raise CoindeskAPIClientError(msg)


class CoindeskAPIHttpResponse(object):
    """
    Enable Coindesk API response data parsing.
    """

    def __init__(self, response={}):
        """
        Initialize Coindesk API http response.

        :param dict response: response data from Coindesk API.
        """
        self.response = response
        for key, value in response.items():
            setattr(self, key, value)

    def __str__(self):
        """
        Represent class via params string.

        :return str: class representation.
        """
        classname = self.__class__.__name__
        return f'<{classname} - Coindesk api response>'

    @classmethod
    def parse(cls, response, data_type=None, currency=None):
        """
        Parse http response from Coindesk API.

        :param dict response: response data from Coindesk API.
        :param str data_type: type of data to fetch (currentprice, historical).
        :param str currency: currency to fetch data in.
        """
        if isinstance(response, (dict, str)):
            try:
                if not isinstance(response, dict):
                    response = json.loads(response)
            except (OverflowError, TypeError) as err:
                msg = f'Could not decode response. {err.args[0]}.'
                logger.error(f'[CoindeskAPIHttpResponse] Response error. {msg}')
                raise CoindeskAPIHttpResponseError(msg)

        schema = utils.get_schema(data_type, currency)
        cls._validate_response(response, schema)
        return cls(response)

    @staticmethod
    def _validate_response(response, schema):
        """
        Validate http response from Coindesk API.

        :param dict response: json response from API.
        :param dict schema: response schema to validate.
        """
        try:
            return jsonschema.validate(response, schema)
        except (SchemaError, ValidationError) as err:
            msg = err.args[0]
            logger.error(f'[CoindeskAPIHttpResponse] Response error. {msg}.')
            raise CoindeskAPIHttpResponseError(msg)

    def get_response_item(self, item):
        """
        Get Coindesk response particular item value.

        :param str item: response item name.
        :return *: corresponding response item value.
        """
        if item not in self.response.keys():
            msg = f'Provided response item {item} does not exist.'
            logger.warning(f'[CoindeskAPIHttpResponse] Invalid response item. {msg}')
        return vars(self).get(item)

    @property
    def response_items(self):
        """
        Get Coindesk response items list.

        :return list: list of response items.
        """
        return list(self.response.keys())

    @property
    def json_response(self):
        """
        Get json response from Coindesk API.

        :return json: json serialized response.
        """
        try:
            return json.dumps(self.response)
        except (OverflowError, TypeError) as err:
            msg = f'Could not encode json response. {err.args[0]}.'
            logger.error(f'[CoindeskAPIHttpResponse] Response error. {msg}')
            raise CoindeskAPIHttpResponseError(msg)
