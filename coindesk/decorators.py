# encoding: utf-8

import asyncio
from functools import wraps
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

# Custom logger for decorators module
fileConfig(join(dirname(dirname(__file__)), 'logging.cfg'))
logger = getLogger(__name__)


def async_event_loop(method):
    @wraps(method)
    def result(self, *args, **kwargs):
        caller = self.__class__.__name__
        logger.info(f'[{caller}] Event loop initialized.')
        response = asyncio.run(method(self, *args, **kwargs))
        logger.info(f'[{caller}] Event loop finished.')
        return response
    return result
