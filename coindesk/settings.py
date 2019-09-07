# encoding: utf-8

from .utils import find_version

# Coindesk API client settings
API_CLIENT_VERSION = find_version('__init__.py')
API_PROTOCOL = 'https'
API_HOST = 'api.coindesk.com'
API_PATH = '/v1/bpi'
API_CURRENTPRICE_DATA_TYPE = 'currentprice'
API_HISTORICAL_DATA_TYPE = 'historical'
API_SUPPORTED_CURRENCIES_DATA_TYPE = 'supported-currencies'
API_CURRENTPRICE_ENDPOINT = f'{API_CURRENTPRICE_DATA_TYPE}' + '{currency}.json'
API_HISTORICAL_ENDPOINT = f'{API_HISTORICAL_DATA_TYPE}/close.json'
API_SUPPORTED_CURRENCIES_ENDPOINT = f'{API_SUPPORTED_CURRENCIES_DATA_TYPE}.json'
API_ENDPOINTS = {
    API_CURRENTPRICE_DATA_TYPE: API_CURRENTPRICE_ENDPOINT,
    API_HISTORICAL_DATA_TYPE: API_HISTORICAL_ENDPOINT,
    API_SUPPORTED_CURRENCIES_DATA_TYPE: API_SUPPORTED_CURRENCIES_ENDPOINT,
}

# Coindesk API valid parameters
INDEX_PARAM = 'index'
CURRENCY_PARAM = 'currency'
START_PARAM = 'start'
END_PARAM = 'end'
FOR_PARAM = 'for'
VALID_DATA_TYPES = [
    API_CURRENTPRICE_DATA_TYPE,
    API_HISTORICAL_DATA_TYPE,
]
VALID_CURRENTPRICE_PARAMS = [
    CURRENCY_PARAM,
]
VALID_HISTORICAL_PARAMS = [
    INDEX_PARAM,
    CURRENCY_PARAM,
    START_PARAM,
    END_PARAM,
    FOR_PARAM,
]
VALID_INDEX = [
    'USD',
    'CNY',
]
VALID_FOR = [
    'yesterday',
]

# Coindesk API client request configuration parameters
REQUEST_MAX_RETRIES = 10
REQUEST_MAX_TIMEOUT = 30
REQUEST_HEADERS = {
    'Accept': 'application/json',
    'Accept-Language': 'en-US',
    'Cache-Control': 'no-cache',
    'Connection': 'close',
    'X-API-client-version': API_CLIENT_VERSION
}
