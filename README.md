# coindesk-api-client

Powered by [![CoinDesk]()](https://www.coindesk.com/api/)

Client written in Python3 for CoinDesk API service:

### Features

  - Get Bitcoin current price
  - Get Bitcoin historical price

### Getting Started

These instructions will get you a copy of the project on your local system.

#### Prerequisites

CoinDesk API Client uses a number of open source projects to work properly:

* [jsonschema] - An implementation of JSON Schema validation for Python
* [requests] - Python HTTP for Humans

And of course CoinDesk API Client itself is open source with a [public repository][coindesk-api-client] on GitHub.

#### Installation

#### Quick Start

A step by step series of examples:

Get currentprice price for Bitcoin in json format
```python
from coindesk.client import CoindeskAPIClient
api_client = CoindeskAPIClient.start('currentprice')
response = api_client.get()
```

Get currentprice price for Bitcoin in other currency than USD
```python
from coindesk.client import CoindeskAPIClient
api_client = CoindeskAPIClient.start('currentprice', {'currency': 'EUR'})
response = api_client.get()
```

Get historical price for Bitcoin in json format
```python
from coindesk.client import CoindeskAPIClient
api_client = CoindeskAPIClient.start('historical')
response = api_client.get()
```

Get historical price for Bitcoin providing optional parameters
```python
from coindesk.client import CoinDeskAPIClient
api_client = CoindeskAPIClient.start('historical', {'start': '2018-01-01', 'end': '2018-03-25'})
response = api_client.get()
```

Get supported currencies to fetch Bitcoin price in
```python
from coindesk.client import CoindeskAPIClient
api_client = CoindeskAPIClient()
supported_currencies = api_client.get_supported_currencies()
```

Full documentation for CoinDesk API is available at https://www.coindesk.com/api/.

License
----

MIT


**Free Software. Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen.)

   [coindesk-api-client]: <https://github.com/sdediego/coindesk-api-client>
   [jsonschema]: <https://github.com/Julian/jsonschema>
   [requests]: <https://github.com/requests/requests>
