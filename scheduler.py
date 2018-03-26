#!/usr/bin/env python
# encoding: utf-8

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job(id='currentprice', trigger='interval', minutes=1)
def currentprice_job():
    """
    Get and save current price data from CoinDesk API.
    """
    pass

@sched.scheduled_job(id='historical', trigger='cron', day_of_week='mon-sun', hour=0)
def historical_job():
    """
    Get and save historical price data from CoinDesk API.
    """
    pass


# Start queueing jobs
sched.start()
