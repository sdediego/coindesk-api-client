#!/usr/bin/env python
# encoding: utf-8

import logging
import os

from dotenv import load_dotenv
from functools import partial
from json import JSONDecoder
from logging.config import fileConfig
from os.path import basename, dirname, join

from .exceptions import JSONFileWriterPipelineError

# Custom logger for spiders module
fileConfig(join(dirname(dirname(__file__)), 'logging.cfg'))
logger = logging.getLogger(__name__)

# Load .env file
dotenv_path = join(dirname(dirname(__file__)), '.env')
load_dotenv(dotenv_path)


class JSONFileWriterPipeline(object):
    """
    Enable persist data in JSON file.
    """
    pass


class MongoDBPipeline(object):
    """
    Enable persist data in MongoDB.
    """
    pass


class PostgreSQLPipeline(object):
    """
    Enable persist data in PostgreSQL database.
    """
    pass
