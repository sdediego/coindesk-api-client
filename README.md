# coindesk-api-client

Powered by [![CoinDesk]()](https://www.coindesk.com/api/)

Client written in Python 3 for CoinDesk API service:

### Features

  - Get Bitcoin current price
  - Get Bitcoin historical price

You can also:

  - Persist data via JSON format file pipeline
  - Persist data via [MongoDB][mongoDB] pipeline
  - Persist data via [PostgreSQL][postgreSQL] pipeline
  - Automatize data fetching with jobs scheduler
  - Deploy to [Heroku cloud platform][heroku]

### Getting Started

These instructions will get you a copy of the project on your local system.

#### Prerequisites

CoinDesk API Client uses a number of open source projects to work properly:

* [apscheduler] - Advanced Python Scheduler
* [configparser] - Configuration file parser
* [psycopg2] - PostgreSQL adapter fo Python
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
response = api.call()
```

Get historical price for Bitcoin
```
api = CoinDeskAPI.config('historical')
response = api.call()
```

Get historical price for Bitcoin providing optional parameters
```
api = CoinDeskAPI.config('historical')
response = api.call(currency='EUR', start='2018-01-01', end='2018-03-03')
```

Persist data in JSON file
```
file = JSONFileWriterPipeline.config()
file.write(response)
```

Persist (save or update) data with MongoDB
```
mongo = MongoDBPipeline.config()
mongo.open_connection()
mongo.persist_data(response)
mongo.close_connection()
```

Full documentation for CoinDesk API is available at https://www.coindesk.com/api/.

License
----

MIT


**Free Software. Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen.)

   [apscheduler]: <https://github.com/agronholm/apscheduler>
   [coindesk-api-client]: <https://github.com/sdediego/coindesk-api-client>
   [configparser]: <https://github.com/python/cpython/blob/3.5/Lib/configparser.py>
   [heroku]: <https://www.heroku.com>
   [mongoDB]: <https://www.mongodb.com>
   [postgreSQL]: <https://www.postgresql.org/>
   [psycopg2]: <http://initd.org/psycopg/>
   [pymongo]: <https://github.com/mongodb/mongo-python-driver>
   [python-dotenv]: <https://github.com/theskumar/python-dotenv>
   [requests]: <https://github.com/requests/requests>
