# encoding: utf-8

class BaseError(Exception):
    """
    Handle generic exception.
    """

    def __init__(self, message: str = None, code: int = None):
        """
        Initialize Base error class.

        :param str message: error description message.
        :param int code: error code number.
        """
        if code is not None:
            message = f'Error {code}: {message}.'

        super(BaseError, self).__init__(message)
        self.code = code
        self.message = message


class CoindeskAPIClientError(BaseError):
    """
    Handle exception for Coindesk API client.
    """
    pass


class CoindeskAPIHttpRequestError(BaseError):
    """
    Handle exception for Coindesk API request.
    """
    pass


class CoindeskAPIHttpResponseError(BaseError):
    """
    Handle exception for Coindesk API response.
    """
    pass
