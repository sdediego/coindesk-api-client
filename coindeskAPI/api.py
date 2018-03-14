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
    pass


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
