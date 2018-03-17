#!/usr/bin/env python
# encoding: utf-8


class BaseError(Exception):
    """
    Handle generic exception.
    """

    def __init__(self, msg, code=None):
        if code is not None:
            self.code = code
            msg += ': {exception}'.format(exception=self.code)
        self.msg = msg
        super(BaseError, self).__init__(self.msg)


class CoinDeskAPIError(BaseError):
    """
    Handle exception for CoinDesk API.
    """
    pass


class CoinDeskAPIHttpRequestError(BaseError):
    """
    Handle exception for CoinDesk API request error.
    """
    pass


class CoinDeskAPIHttpResponseError(BaseError):
    """
    Handle exception for CoinDesk API response error.
    """
    pass
