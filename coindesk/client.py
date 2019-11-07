# encoding: utf-8

import asyncio
import json
import math
import re
from collections import OrderedDict
from json import JSONDecodeError
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

import aiohttp
import jsonschema
import requests
from aiohttp import ClientResponse, ClientSession
from furl import furl as URL
from jsonschema import SchemaError, ValidationError
from requests.exceptions import RequestException

from . import settings, utils
from .decorators import async_event_loop
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

    def __init__(self, retries: int = 10, redirects: bool = True, timeout: int = 5, backoff: bool = True):
        """
        Initialize Coindesk API http request making.

        :param int retries: number of request attempts before failing.
        :param bool redirects: enable/disable http verbs redirection.
        :param int timeout: seconds before request timeout.
        :param bool backoff: enable/disable http request retry backoff.
        """
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
    def start(cls, retries: int = 10, redirects: bool = True, timeout: int = 5, backoff: bool = True):
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
    def validate(retries: int, redirects: bool, timeout: int, backoff: bool):
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
    def retries(self, retries: int):
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
    def redirects(self, redirects: bool):
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
    def timeout(self, timeout: int):
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
    def backoff(self, backoff: bool):
        """
        Set/unset request backoff.

        :param bool backoff: enable/disable http requests backoff.
        """
        backoff = utils.validate_backoff(backoff)
        self._backoff = backoff

    @async_event_loop
    async def get(self, url: str, raw: bool = False):
        """
        Retrieve response object/data from Coindesk API url.

        :param str url: api resource locator.
        :param bool raw: enable/disable api response parsing.
        :return *: api http raw response or response data.
        """
        options = self._get_request_options()
        async with aiohttp.ClientSession() as session:
            response = await self._http_request(session, url, options)
        self._check_response_status(response)
        return response if raw else await self._get_json_response(response)

    def _get_request_options(self):
        """
        Return http get request option parameters.
        """
        return {
            'headers': OrderedDict(settings.REQUEST_HEADERS),
            'allow_redirects': self.redirects,
            'timeout': self.timeout
        }

    async def _http_request(self, session: ClientSession, url: str, options: dict):
        """
        Make asynchronous http request to Coindesk API.

        :param obj session: client session.
        :param str url: optional query parameters.
        :param dict options: http request options.
        :return obj: http response object.
        """
        for retry in range(1, self.retries + 1):
            try:
                return await session.get(url, **options)
            except RequestException as err:
                timeout = self._wait_exp_backoff(retry) if self.backoff else 0
                logger.error(f'[CoindeskAPIHttpRequest] Retry {retry} request. {err.args[0]}.')
                logger.error(f'[CoindeskAPIHttpRequest] Waiting {timeout} ms.')
                await asyncio.sleep(timeout / 10)
        else:
            msg = f'No response from Coindesk API url {url}.'
            logger.error(f'[CoindeskAPIHttpRequest] Request error. {msg}')
            raise CoindeskAPIHttpRequestError(msg)

    def _wait_exp_backoff(self, retry: int):
        """
        Calculate exponential backoff time.

        :param int retries: number of request attempts before failing.
        :return int: time to wait between http requests retries.
        """
        return math.pow(2, retry)

    def _check_response_status(self, response: ClientResponse):
        """
        Verify http response status code.

        :param int status: http response status code.
        """
        status = str(response.status)
        msg = f'Status code {status} - {response.reason}.'
        if status.startswith('1'):
            logger.info(f'[CoindeskAPIHttpRequest] Request info. {msg}')
        elif status.startswith('2'):
            logger.info(f'[CoindeskAPIHttpRequest] Request success. {msg}')
        elif status.startswith('3'):
            logger.info(f'[CoindeskAPIHttpRequest] Request redirect. {msg}')
        elif status.startswith('4'):
            logger.error(f'[CoindeskAPIHttpRequest] Client error. {msg}')
            raise CoindeskAPIHttpRequestError(msg)
        elif status.startswith('5'):
            logger.error(f'[CoindeskAPIHttpRequest] Server error. {msg}')
            raise CoindeskAPIHttpRequestError(msg)

    async def _get_json_response(self, response: ClientResponse):
        """
        Return response json data format.

        :param obj response: http response object.
        :return json: response json data.
        """
        try:
            data = await response.json(content_type=None)
        except JSONDecodeError as err:
            msg = f'Could not decode json data. {err.args[0]}.'
            logger.error(f'[CoindeskAPIHttpRequest] Request error. {msg}')
            raise CoindeskAPIHttpRequestError(msg)
        logger.info('[CoindeskAPIHttpRequest] JSON data decoded.')
        return data


class CoindeskAPIClient(CoindeskAPIHttpRequest):
    """
    Enable Coindesk API use.
    """

    def __init__(self, data_type: str = None, params: dict = None, retries: int = 10,
                 redirects: bool = True, timeout: int = 5, backoff: bool = True):
        """
        Initialize Coindesk API client.

        :param str data_type: type of data to fetch (currentprice, historical).
        :param dict params: optional url query parameters.
        :param int retries: number of request attempts before failing.
        :param bool redirects: enable/disable http verbs redirection.
        :param int timeout: seconds before request timeout.
        :param bool backoff: enable/disable http request retry backoff.
        """
        if params is None: params = {}
        super(CoindeskAPIClient, self).__init__(retries, redirects, timeout, backoff)
        self._data_type = data_type
        self._api_endpoint = self._construct_api_endpoint(data_type, params)

    def __str__(self):
        """
        Represent class via params string.

        :return str: class representation.
        """
        classname = self.__class__.__name__
        endpoint = self._api_endpoint
        return f'<{classname} - Coindesk api client\nendpoint: {endpoint}>'

    @classmethod
    def start(cls, data_type: str = None, params: dict = None, retries: int = 10,
              redirects: bool = True, timeout: int = 5, backoff: bool = True):
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
        if params is None: params = {}
        data_type = utils.validate_data_type(data_type)
        params = utils.validate_params(data_type, params)
        retries, redirects, timeout, backoff = cls.validate(retries, redirects, timeout, backoff)
        return cls(data_type, params, retries, redirects, timeout, backoff)

    def _construct_api_endpoint(self, data_type: str, params: dict):
        """
        Get Coindesk api endpoint.

        :param str data_type: type of data to fetch (currentprice, historical).
        :param dict params: optional query parameters.
        :return str: Coindesk api endpoint for correspondig data resource.
        """
        scheme, host, path = self._get_api_url_components()
        resource = settings.API_ENDPOINTS.get(data_type)
        if data_type == settings.API_CURRENTPRICE_DATA_TYPE:
            currency_param = params.pop(settings.CURRENCY_PARAM, '')
            currency = f'/{currency_param}' if currency_param else currency_param
            resource = resource.format(currency=currency)
        path = f'{path}/{self._clean_api_component(resource)}'
        api_endpoint = URL(scheme=scheme, host=host, path=path, args=params)
        utils.validate_url(api_endpoint.url)
        return api_endpoint

    def _get_api_url_components(self):
        """
        Get Coindesk api base url components.

        :return list: Coindesk api base url components.
        """
        components = settings.API_PROTOCOL, settings.API_HOST, settings.API_PATH
        return [self._clean_api_component(component) for component in components]

    def _clean_api_component(self, component: str):
        """
        Clean Coindesk api base url components.

        :param str component: Coindesk api base url component.
        :return str: Coindesk api base url cleaned component.
        """
        return re.sub('://', '', component).strip('/')

    @property
    def data_type(self):
        """
        Get Coindesk data type resource.
        """
        return self._data_type

    @data_type.setter
    def data_type(self, data_type: str):
        """
        Set Coindesk API client data type and corresponding api path attribute.

        :param str data_type: type of data to fetch (currentprice, historical).
        """
        self._data_type = utils.validate_data_type(data_type)
        self._api_endpoint = self._construct_api_endpoint(data_type, {})

    @property
    def url(self):
        """
        Get Coindesk api endpoint.
        """
        return self._api_endpoint.url

    @property
    def origin(self):
        """
        Get Coindesk api endpoint origin.
        """
        return self._api_endpoint.origin

    @property
    def path(self):
        """
        Get Coindesk api endpoint path.
        """
        return str(self._api_endpoint.path)

    @property
    def params(self):
        """
        Get Coindesk api endpoint optional query parameters.
        """
        if self.data_type == settings.API_CURRENTPRICE_DATA_TYPE:
            if self.path.endswith('currentprice.json'): return []
            currency = self._api_endpoint.path.segments[-1].rstrip('.json')
            return [('currency', currency)]
        elif self.data_type == settings.API_HISTORICAL_DATA_TYPE:
            return self._api_endpoint.query.params.items()

    @params.setter
    def params(self, params: dict):
        """
        Set Coindesk API client optinal query parameters.
        This will overwrite all existing params.

        :param dict params: optional url query parameters.
        """
        params = utils.validate_params(self.data_type, params)
        if self.data_type == settings.API_CURRENTPRICE_DATA_TYPE:
            self._api_endpoint = self._construct_api_endpoint(self.data_type, params)
        elif self.data_type == settings.API_HISTORICAL_DATA_TYPE:
            self._api_endpoint.query.params = params

    def has_param(self, key: str):
        """
        Check if Coindesk API endpoint has certain param.

        :param str key: query param name.
        :return bool: true/false has param response.
        """
        has_param = key in self._api_endpoint.query.params
        if self.data_type == settings.API_CURRENTPRICE_DATA_TYPE and key == settings.CURRENCY_PARAM:
            has_param = not self.path.endswith('currentprice.json')
        return has_param

    def add_param(self, param: dict):
        """
        Add Coindesk API client optinal query parameter.

        :param dict param: optional url query parameter.
        """
        param = utils.validate_params(self.data_type, param)
        if self.data_type == settings.API_CURRENTPRICE_DATA_TYPE:
            self._api_endpoint = self._construct_api_endpoint(self.data_type, param)
        elif self.data_type == settings.API_HISTORICAL_DATA_TYPE:
            key = list(param.keys())[0]
            if self.has_param(key): self.delete_param(key)
            self._api_endpoint.add(args=param)

    def add_many_params(self, params: dict):
        """
        Add many Coindesk API client optinal query parameters.

        :param dict params: optional url query parameters.
        """
        for key, value in params.items():
            self.add_param({key: value})

    def delete_param(self, key: str):
        """
        Delete Coindesk API client optinal query parameter.

        :param str param: optional url query parameter.
        """
        deleted_param = None
        if self.data_type == settings.API_CURRENTPRICE_DATA_TYPE:
            if not self.path.endswith('currentprice.json'):
                segments = self._api_endpoint.path.segments
                self._api_endpoint.path = f'{"/".join(segments[:-1])}.json'
                deleted_param = segments[-1].rstrip('.json')
        elif self.data_type == settings.API_HISTORICAL_DATA_TYPE:
            deleted_param = self._api_endpoint.query.params.pop(param, None)

        if deleted_param is None:
            msg = f'Query parameter {param} does not exist.'
            logger.warning(f'[CoindeskAPIClient] Delete param. {msg}')
        return deleted_param

    def delete_many_params(self, keys: list):
        """
        Delete many Coindesk API client optinal query parameters.

        :param list params: optional url query parameters.
        """
        for key in keys:
            self.delete_param(key)

    @property
    def valid_params(self):
        """
        Get Coindesk valid query parameters for api endpoint.
        """
        if self.data_type == settings.API_CURRENTPRICE_DATA_TYPE:
            return settings.VALID_CURRENTPRICE_PARAMS
        elif self.data_type == settings.API_HISTORICAL_DATA_TYPE:
            return settings.VALID_HISTORICAL_PARAMS
        else:
            msg = f'Uncorrect data type setup for {self.data_type}.'
            logger.warning(f'[CoindeskAPICient] Data type error. {msg}')
            return None

    def get_supported_currencies(self):
        """
        Get Coindesk valid currencies list.
        """
        scheme, host, path = self._get_api_url_components()
        resource = settings.API_ENDPOINTS.get('supported-currencies')
        path = f'{path}/{self._clean_api_component(resource)}'
        url = URL(scheme=scheme, host=host, path=path)
        currencies = None
        try:
            utils.validate_url(url.url)
            currencies = super(CoindeskAPIClient, self).get(url.url, False)
        except Exception as err:
            msg = err.args[0]
            logger.warning(f'[CoindeskAPICient] Get currencies error. {msg}.')

        if currencies: utils.validate_currencies_settings(currencies)
        return currencies if currencies else utils.get_currencies_settings()

    def get(self, raw: bool = False):
        """
        Make http get request to Coindesk API.

        :param bool raw: enable/disable api response parsing.
        :return *: api http raw response or data.
        """
        try:
            return super(CoindeskAPIClient, self).get(self.url, raw)
        except Exception as err:
            msg = err.args[0]
            logger.error(f'[CoindeskAPICient] API call error. {msg}.')
            raise CoindeskAPIClientError(msg)


class CoindeskAPIHttpResponse(object):
    """
    Enable Coindesk API response data parsing.
    """

    def __init__(self, response: dict = None):
        """
        Initialize Coindesk API http response.

        :param dict response: response data from Coindesk API.
        """
        self.response = response if response is not None else {}
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
    def parse(cls, response: dict = None, data_type: str = None, currency: str = None):
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
        else:
            msg = 'Response data type must be dict or str.'
            logger.error(f'[CoindeskAPIHttpResponse] Response error. {msg}')
            raise CoindeskAPIHttpResponseError(msg)

        schema = utils.get_schema(data_type, currency)
        cls._validate_response(response, schema)
        return cls(response)

    @staticmethod
    def _validate_response(response: dict, schema: dict):
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

    def get_response_item(self, item: str):
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
