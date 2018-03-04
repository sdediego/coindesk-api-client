#!/usr/bin/env python
# encoding: utf-8


class CoinDeskAPIError(Exception):
    """
    Handle exception for CoinDesk API.
    """

    def __init__(self, msg, code=None):
        if code is not None:
            self.code = code
            msg += ': {exception}'.format(exception=self.code)
        self.msg = msg
        super(CoinDeskAPIError, self).__init__(self.msg)


class CoinDeskAPIHttpRequestError(CoinDeskAPIError):
    """
    Handle exception for CoinDesk API request error.
    """
    pass


class CoinDeskAPIHttpResponseError(CoinDeskAPIError):
    """
    Handle exception for CoinDesk API response error.
    """
    pass