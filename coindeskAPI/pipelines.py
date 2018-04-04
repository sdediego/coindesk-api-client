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

# Custom logger
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
        filepath = os.getenv('JSON_FILE_PATH')
        if filepath is not None:
            return cls(filepath)
        else:
            msg = 'Incorrect JSON file configuration: {}'.format(filepath)
            raise ValueError(msg)

    def write(self, data):
        """
        Open file connection and write data.
        """
        with open(self._file, 'a') as json_file:
            json.dump(data, json_file, indent=2)
            json_file.write('\n\n')

    def read(self):
        """
        Open file connection and read data.

        :return list: list with json objects.
        """
        with open(self._file, 'r') as json_file:
            return list(self._parse(json_file))

    def _parse(self, file, decoder=JSONDecoder(), delimeter='\n', buffer_size=2048):
        """
        Yield complete JSON objects as the parser finds them.

        :param obj file: json file object to parse.
        :param obj decoder: json decoder instance.
        :param str delimeter: json objects delimeter in file.
        :param int buffer_size: buffer size in bytes.
        """
        buffer = ''
        for chunk in iter(partial(file.read, buffer_size), ''):
            buffer += chunk
            while buffer:
                try:
                    stripped = buffer.strip(delimeter)
                    result, index = decoder.raw_decode(stripped)
                    yield result
                    buffer = stripped[index:]
                except ValueError:
                    break


class MongoDBPipeline(object):
    """
    Enable persist data in MongoDB.
    """

    def __init__(self, mongo_url, mongo_db, mongo_collection):
        """
        Initialize MongoDB class config.

        :param str mongo_url: MongoDB locator.
        :param str mongo_db: MongoDB name.
        :param str mongo_collection: MongoDB collection name.
        """
        self._mongo_url = mongo_url
        self._mongo_db = mongo_db
        self._mongo_collection = mongo_collection
        self._mongo_uri = self._mongo_url + self._mongo_db

    def __str__(self):
        """
        Represent class via params string.

        :return str: class representation.
        """
        params = {
            'classname': self.__class__.__name__,
            'url': self._mongo_url,
            'db': self._mongo_db,
            'collection': self._mongo_collection,
        }
        return str(params)

    @classmethod
    def config(cls):
        """
        Get MongoDB configuration parameters.

        :return cls: MongoDBPipeline class.
        """
        mongo_config = {
            'mongo_url': os.getenv('MONGO_URL'),
            'mongo_db': os.getenv('MONGO_DB'),
            'mongo_collection': os.getenv('MONGO_COLLECTION'),
        }
        if None not in mongo_config.values():
            return cls(**mongo_config)
        else:
            msg = 'Incorrect MongoDB configuration: {}'.format(mongo_config)
            raise ValueError(msg)

    def open_connection(self):
        """
        Establish MongoDB client connection.
        """
        self.client = pymongo.MongoClient(self._mongo_uri)
        if self.client is None:
            raise ConnectionFailure('Connection uri: {}'.format(self._mongo_uri))
        self.db = self.client[self._mongo_db]
        self.collection = self.db[self._mongo_collection]

    def close_connection(self):
        """
        Close MongoDB client connection.
        """
        self.client.close()

    def persist_data(self, data):
        """
        Persist data in MongoDB.

        :param json data: json data to persist.
        :return json: persisted data in MongoDB.
        """
        data = json.loads(data)
        for key, value in data.items():
            if not value:
                raise ValueError('Missing value for {}'.format(key))

        if 'USD' in data.get('bpi'):
            data.update({'name': 'currentprice'})
        else:
            data.update({'name': 'historical'})

        try:
            data_found = self.collection.find_one(
                {'name': data.get('name')},
                {'name': 1, '_id': 0}
            )
            if data_found:
                return self._update(data)
            return self._insert(data)
        except PyMongoError as msg:
            logger.error('Database operation failure: %s', msg)

    def _insert(self, data):
        pass

    def _update(self, data):
        pass


class PostgreSQLPipeline(object):
    """
    Enable persist data in PostgreSQL database.
    """
    pass
