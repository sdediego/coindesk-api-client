#!/usr/bin/env python
# encoding: utf-8

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date
from logging.config import fileConfig
from os.path import dirname, join

from coindesk.api import CoinDeskAPIClient
from coindesk.pipelines import MongoDBPipeline

# Custom logger for spiders module
fileConfig(join(dirname(dirname(__file__)), 'logging.cfg'))
logger = logging.getLogger(__name__)

sched = BlockingScheduler()


def retrieve_and_persit_data(data):
    """
    Get and save data from CoinDesk API.

    :param str data: type of data (currentprice, historical).
    """
    # Retrieve currentprice/historical data
    kwargs = {}
    api = CoinDeskAPIClient.config(data)
    if data == 'historical':
        today = date.today().strftime("%Y-%m-%d")
        kwargs.update({'start': '2010-01-01', 'end': today})
    result = api.call(**kwargs)

    # Persist retrieved data
    logger.info('Persisting fetched data in MongoDB: %s', result)
    mongo = MongoDBPipeline.config()
    mongo.open_connection()
    mongo.persist_data(result)
    mongo.close_connection()
    logger.info('Data successfully persisted.')

@sched.scheduled_job(id='currentprice', trigger='interval', minutes=1)
def currentprice_job():
    """
    Get and save current price data from CoinDesk API.
    """
    logger.info('Fetching current price data.')
    retrieve_and_persit_data('currentprice')

@sched.scheduled_job(id='historical', trigger='cron', day_of_week='mon-sun', hour=0)
def historical_job():
    """
    Get and save historical price data from CoinDesk API.
    """
    logger.info('Fetching historical price data.')
    retrieve_and_persit_data('historical')


# Start queueing jobs
sched.start()
