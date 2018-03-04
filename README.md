# coindesk-api-client

Powered by [![CoinDesk]()](https://www.coindesk.com/api/)

Client written in Python 3 for CoinDesk API service:

### Features

  - Get Bitcoin current price
  - Get Bitcoin historical price

You can also:

  - Persist data via MongoDB pipeline
  - Automatize data fetching with jobs scheduler
  - Deploy to Heroku cloud platform

### Getting Started

These instructions will get you a copy of the project on your local system.

#### Prerequisites

CoinDesk API Client uses a number of open source projects to work properly:

* [requests] - HTTP for Humans
* [apscheduler] - Advanced Python Scheduler
* [configparser] - Configuration file parser
* [pymongo] - Python driver for MongoDB

And of course CoinDesk API Client itself is open source with a [public repository][coindesk-api-client] on GitHub.

#### Installation

#### Quick Start

A step by step series of examples:

Get current price for Bitcoin in json format
```
api = CoinDeskAPI.config('currentprice')
result = api.call()
```

Get historical price for Bitcoin in json format
```
api = CoinDeskAPI.config('historical')
result = api.call()
```

Persist (save/update) data with MongoDB
```
mongo = MongoDBPipeline.config()
mongo.open_connection()
mongo.persist_data(result)
mongo.close_connection()
```

License
----

MIT


**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [coindesk-api-client]: <https://github.com/sdediego/coindesk-api-client>
   [requests]: <https://github.com/requests/requests>
   [apscheduler]: <https://github.com/agronholm/apscheduler>
   [configparser]: <https://github.com/python/cpython/blob/3.5/Lib/configparser.py>
   [pymongo]: <https://github.com/mongodb/mongo-python-driver>
