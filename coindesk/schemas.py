# encoding: utf-8

# Coindesk API response schemas
CURRENTPRICE_SCHEMA = {
    "type": "object",
    "properties": {
        "time": {
            "updated": {"type": "string"},
            "updatedISO": {"type": "string"},
            "updateduk": {"type": "string"}
        },
        "chartName": {"type": "string"},
        "disclaimer": {"type": "string"},
        "bpi": {
            "USD": {
                "code": {"type": "string"},
                "symbol": {"type": "string"},
                "rate": {"type": "string"},
                "description": {"type": "string"},
                "rate_float": {"type": "number"}
            },
            "GBP": {
                "code": {"type": "string"},
                "symbol": {"type": "string"},
                "rate": {"type": "string"},
                "description": {"type": "string"},
                "rate_float": {"type": "number"}
            },
            "EUR": {
                "code": {"type": "string"},
                "symbol": {"type": "string"},
                "rate": {"type": "string"},
                "description": {"type": "string"},
                "rate_float": {"type": "number"}
            }
        }
    },
    "required": ["chartName", "time", "disclaimer", "bpi"]
}

CURRENTPRICE_CODE_SCHEMA = {
    "type": "object",
    "properties": {
        "time": {
            "updated": {"type": "string"},
            "updatedISO": {"type": "string"},
            "updateduk": {"type": "string"}
        },
        "disclaimer": {"type": "string"},
        "bpi": {
            "USD": {
                "code": {"type": "string"},
                "rate": {"type": "string"},
                "description": {"type": "string"},
                "rate_float": {"type": "number"}
            }
        }
    },
    "required": ["time", "disclaimer", "bpi"]
}

HISTORICAL_SCHEMA = {
    "type": "object",
    "properties": {
        "time": {
            "updated": {"type": "string"},
            "updatedISO": {"type": "string"}
        },
        "disclaimer": {"type": "string"},
        "bpi": {"type": "object"}
    },
    "required": ["time", "disclaimer", "bpi"]
}
