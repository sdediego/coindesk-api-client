# encoding: utf-8

import codecs
import json
import re
from datetime import datetime
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from . import schemas, settings
from .exceptions import (CoindeskAPIClientError,
                         CoindeskAPIHttpRequestError,
                         CoindeskAPIHttpResponseError)

# Custom logger for client config module
fileConfig(join(dirname(dirname(__file__)), 'logging.cfg'))
logger = getLogger(__name__)


def validate_data_type(data_type: str):
    """
    Validate data type to request.

    :param str data_type: type of data to fetch (currentprice, historical).
    """
    if data_type not in settings.VALID_DATA_TYPES:
        msg = f'Data must be {" or ".join(settings.VALID_DATA_TYPES)}.'
        logger.error(f'[CoinDeskAPIClient] Data error. {msg}')
        raise CoindeskAPIClientError(msg)
    return data_type


def validate_params(data_type: str, params: dict):
    """
    Validate query parameters of the request.

    :param str data_type: type of data to fetch (currentprice, historical).
    :param dict params: optional query parameters.
    :return dict: validated optional query parameters.
    """
    if data_type == settings.API_CURRENTPRICE_DATA_TYPE:
        for param in params.keys():
            if param not in settings.VALID_CURRENTPRICE_PARAMS:
                msg = f'Unvalid param {param} for {data_type} data.'
                logger.error(f'[CoinDeskAPIClient] Param error. {msg}')
                raise CoindeskAPIClientError(msg)
        if settings.CURRENCY_PARAM in params:
            validate_currency(params[settings.CURRENCY_PARAM])
    elif data_type == settings.API_HISTORICAL_DATA_TYPE:
        for param in params.keys():
            if param not in settings.VALID_HISTORICAL_PARAMS:
                msg = f'Unvalid param {param} for {data_type} data.'
                logger.error(f'[CoinDeskAPIClient] Param error. {msg}')
                raise CoindeskAPIClientError(msg)
        if settings.INDEX_PARAM in params:
            validate_index(params=params)
        if settings.CURRENCY_PARAM in params:
            validate_currency(params=params)
        if settings.START_PARAM in params:
            validate_date(params=params, flag=settings.START_PARAM)
        if settings.END_PARAM in params:
            validate_date(params=params, flag=settings.END_PARAM)
        if settings.FOR_PARAM in params:
            validate_for(params=params)
    else:
        msg = f'Unable to validate params for data {data_type}.'
        logger.error(f'[CoinDeskAPIClient] Data error. {msg}')
        raise CoindeskAPIClientError(msg)
    return params


def validate_index(index: str = None, params: dict = None):
    """
    Validate index query parameter.

    :param str index: index optional url query parameter.
    :param dict params: optional query parameters.
    """
    if params is None: params = {}
    index = index or params.get(settings.INDEX_PARAM)
    if index not in settings.VALID_INDEX:
        msg = f'Index must be {" or ".join(settings.VALID_INDEX)}.'
        logger.error(f'[CoinDeskAPIClient] Index error. {msg}')
        raise CoindeskAPIClientError(msg)


def validate_currency(currency: str = None, params: dict = None):
    """
    Validate currency to request data in.

    :param str currency: currency to fetch data in.
    :param dict params: optional query parameters.
    """
    if params is None: params = {}
    currency = currency or params.get(settings.CURRENCY_PARAM)
    currencies = list(map(lambda c: c['currency'], get_currencies_settings()))
    if currency is not None and currency not in currencies:
        msg = f'Unvalid provided currency {currency}.'
        logger.error(f'[CoinDeskAPIClient] Currency error. {msg}')
        raise CoindeskAPIClientError(msg)


def validate_date(date: str = None, params: dict = None, flag: str = None):
    """
    Validate date query parameter.

    :param str date: datetime at which to start/end the chart.
    :param dict params: optional query parameters.
    :param str flag: signalize "start" or "end" date.
    """
    if params is None: params = {}
    date = date or params.get(flag)
    match = re.search(r'^(?P<date>\d{4}-\d{1,2}-\d{1,2})$', date)
    if match:
        try:
            date = datetime.strptime(match.group('date'), '%Y-%m-%d')
            params[flag] = date.strftime('%Y-%m-%d')
        except ValueError as err:
            msg = f'Unable to parse {flag} param. {err.args[0]}.'
            logger.error(f'[CoinDeskAPIClient] Date error. {msg}')
            raise CoindeskAPIClientError(msg)
    else:
        msg = f'{flag.capitalize()} must fullfill the pattern YYYY-MM-DD.'
        logger.error(f'[CoinDeskAPIClient] Date error. {msg}')
        raise CoindeskAPIClientError(msg)


def validate_for(for_param: str = None, params: dict = None):
    """
    Validate for query parameter.

    :param str for: datetime signaling previous day data.
    :param dict params: optional query parameters.
    """
    if params is None: params = {}
    for_param = for_param or params.get(settings.FOR_PARAM)
    if for_param not in settings.VALID_FOR:
        msg = f'For must be {settings.VALID_FOR[0]}.'
        logger.error(f'[CoinDeskAPIClient] For error. {msg}')
        raise CoindeskAPIClientError(msg)


def validate_retries(retries: int):
    """
    Validate request retries attempt parameter.

    :param int retries: number of request attempts before failing.
    :return int: retries number.
    """
    if type(retries) is not int or retries < 0:
        msg = 'Retries must be zero or positive integer number.'
        logger.error(f'[CoindeskAPIHttpRequest] Retries error. {msg}')
        raise CoindeskAPIHttpRequestError(msg)
    max_retries = min(retries, settings.REQUEST_MAX_RETRIES)
    if max_retries < retries:
        logger.warning(f'[CoinDeskAPIClient] Request max retries. {max_retries}.')
    return max_retries


def validate_redirects(redirects: bool):
    """
    Validate http request redirects.

    :param bool redirects: enable/disable http verbs redirection.
    :return bool: redirects status.
    """
    if not isinstance(redirects, bool):
        msg = 'Redirects must be boolean.'
        logger.error(f'[CoindeskAPIHttpRequest] Redirects error. {msg}')
        raise CoindeskAPIHttpRequestError(msg)
    return redirects


def validate_timeout(timeout: int):
    """
    Validate request timeout.

    :param int timeout: number seconds of request timeout.
    :return int: timeout seconds number.
    """
    if type(timeout) is not int or timeout < 0:
        msg = 'Timeout must be zero or positive integer number.'
        logger.error(f'[CoindeskAPIHttpRequest] Timeout error. {msg}')
        raise CoindeskAPIHttpRequestError(msg)
    max_timeout = min(timeout, settings.REQUEST_MAX_TIMEOUT)
    if max_timeout < timeout:
        logger.warning(f'[CoinDeskAPIClient] Request max retries. {max_timeout}.')
    return max_timeout


def validate_backoff(backoff: bool):
    """
    Validate http request backoff.

    :param bool backoff: enable/disable http request backoff.
    :return bool: backoff status.
    """
    if not isinstance(backoff, bool):
        msg = 'Backoff must be boolean.'
        logger.error(f'[CoindeskAPIHttpRequest] Backoff error. {msg}')
        raise CoindeskAPIHttpRequestError(msg)
    return backoff


def validate_url(url: str):
    """
    Validate Coindesk constructed url.

    :param str url: Coindesk api endpoint.
    """
    regex = re.compile(
        r'^(?:http)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))'
        r'(?:[/?#][^\s]*)?$', re.IGNORECASE)
    match = regex.search(url)
    if not match:
        msg = f'Invalid url {url}.'
        logger.error(f'[CoinDeskAPIClient] Url error. {msg}')
        raise CoindeskAPIClientError(msg)
    return url


def validate_currencies_settings(currencies: list):
    """
    Validate supported currencies settings against feched ones.

    :param list currencies: Coindesk API supported currencies.
    """
    codes = list(map(lambda c: c['currency'], get_currencies_settings()))
    supported_codes = list(map(lambda c: c['currency'], currencies))
    if not set(codes) == set(supported_codes):
        msg = 'Valid currencies settings out of date.'
        logger.warning(f'[CoindeskAPIHttpRequest] Currencies warn. {msg}')
        update_currencies_settings(currencies)


def get_currencies_settings():
    """
    Get supported currencies settings list.

    :return list: valid currencies list from settings file.
    """
    currencies_json = join(dirname(__file__), 'currencies.json')
    try:
        with open(currencies_json) as currencies_file:
            currencies = json.load(currencies_file)
    except (OSError, IOError) as err:
        msg = f'Unable to read currencies file. {err.args[0]}.'
        logger.error(f'[CoindeskAPIClient] File error. {msg}')
        raise CoindeskAPIClientError(msg)
    return currencies.get('SUPPORTED_CURRENCIES')


def update_currencies_settings(currencies: list):
    """
    Get supported currencies settings list.

    :param list currencies: Coindesk API supported currencies.
    """
    currencies_json = join(dirname(__file__), 'currencies.json')
    supported_currencies = {'SUPPORTED_CURRENCIES': currencies}
    try:
        with open(currencies_json, 'w') as outfile:
            json.dump(supported_currencies, outfile, indent=2)
    except (OSError, IOError) as err:
        msg = f'Unable to write currencies file. {err.args[0]}.'
        logger.error(f'[CoindeskAPIClient] File error. {msg}')
        raise CoindeskAPIClientError(msg)
    msg = 'Currencies file successfully updated.'
    logger.info(f'[CoindeskAPIClient] File updated. {msg}')


def get_schema(data_type: str, currency: str = None):
    """
    Get schema for corresponding data and currency.

    :param str data_type: type of data to fetch (currentprice, historical).
    :param str currency: code for allowed currency.
    :return dict: CoinDesk API response schema.
    """
    schema = {}
    if data_type == settings.API_CURRENTPRICE_DATA_TYPE:
        if currency is not None:
            schema = get_schema_for_currency(currency)
        else:
            schema = schemas.CURRENTPRICE_SCHEMA
    elif data_type == settings.API_HISTORICAL_DATA_TYPE:
        schema = schemas.HISTORICAL_SCHEMA

    if not schema:
        msg = f'No schema for data type {data_type} and currency {currency}.'
        logger.error(f'[CoinDeskAPIHttpResponse] Schema error. {msg}')
        raise CoindeskAPIHttpResponseError(msg)
    return schema


def get_schema_for_currency(currency: str):
    """
    Set currentprice schema for specific currency.

    :param str currency: code for allowed currency.
    :return dict: Updated schema for currency.
    """
    schema = schemas.CURRENTPRICE_CODE_SCHEMA
    schema["properties"]["bpi"].update({
        currency: {
            "code": {"type": "string"},
            "symbol": {"type": "string"},
            "description": {"type": "string"},
            "rate_float": {"type": "number"}
        }
    })
    return schema


def find_version(*path_parts):
    """
    Get current coindesk api client version.

    :param tuple path_parts: path parts for version module.
    :return str: api client version.
    """
    version = read(*path_parts)
    match = re.search(r'^__version__ = ["\'](?P<version>[^"\']*)["\']', version, re.M)
    if not match:
        msg = 'Unable to find module version.'
        logger.error(f'[find_version] Setup error. {msg}')
        raise RuntimeError(msg)
    return str(match.group('version'))


def read(*path_parts):
    """
    Get version module.

    :param tuple path_parts: path parts for version module.
    :return obj: module with version.
    """
    base_dir = dirname(__file__)
    file_path = join(base_dir, *path_parts)
    return codecs.open(file_path, encoding='utf-8').read()
