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

    def __init__(self, filepath):
        """
        Initialize JSON file writer class config.

        :param str filepath: json file path.
        """
        self._file = filepath

    def __str__(self):
        """
        Represent class via params string.

        :return str: class representation.
        """
        params = {
            'class': self.__class__.__name__,
            'path': dirname(self._file),
            'filename': basename(self._file),
        }
        return str(params)

    @classmethod
    def config(cls):
        """
        Get JSON file parameters.

        :return cls: JSON file writer class.
        """
        file_config = {
            'filepath': os.getenv('JSON_FILE_PATH'),
        }
        if None not in file_config.values():
            return cls(**file_config)
        else:
            msg = 'Incorrect JSON file configuration: {}'.format(file_config)
            raise ValueError(msg)


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
