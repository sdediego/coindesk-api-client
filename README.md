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

* [apscheduler] - Advanced Python Scheduler
* [configparser] - Configuration file parser
* [pymongo] - Python driver for MongoDB
* [python-dotenv] - .env file management
* [requests] - HTTP for Humans

And of course CoinDesk API Client itself is open source with a [public repository][coindesk-api-client] on GitHub.

#### Installation

#### Quick Start

A step by step series of examples:

Get current price for Bitcoin
```
api = CoinDeskAPI.config('currentprice')
result = api.call()
```

Get historical price for Bitcoin
```
api = CoinDeskAPI.config('historical')
result = api.call()
```

Get historical price for Bitcoin providing optional parameters
```
api = CoinDeskAPI.config('historical')
result = api.call(currency='EUR', start='2018-01-01', end='2018-03-03')
```

Persist (save or update) data with MongoDB
```
mongo = MongoDBPipeline.config()
mongo.open_connection()
mongo.persist_data(result)
mongo.close_connection()
```

Full documentation for CoinDesk API is available at https://www.coindesk.com/api/.

License
----

MIT


**Free Software. Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [apscheduler]: <https://github.com/agronholm/apscheduler>
   [coindesk-api-client]: <https://github.com/sdediego/coindesk-api-client>
   [configparser]: <https://github.com/python/cpython/blob/3.5/Lib/configparser.py>
   [pymongo]: <https://github.com/mongodb/mongo-python-driver>
   [python-dotenv]: <https://github.com/theskumar/python-dotenv>
   [requests]: <https://github.com/requests/requests>
