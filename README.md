# gpswe

![PyPI](https://img.shields.io/pypi/v/clubhouse_api?color=orange) 
![Python 3.7, 3.8, 3.9, 3.10](https://img.shields.io/pypi/pyversions/clubhouse?color=blueviolet) 
![License](https://img.shields.io/pypi/l/clubhouse-api?color=blueviolet)

**gpswe** - this module is a Python client library for work with GPS Trackers (Wialon IPS, EGTS)


## Installation

Install the current version with [PyPI](https://pypi.org/project/clubhouse-api/):

```bash
pip install gpswe
```

Or from Github:
```bash
pip install https://github.com/Peopl3s/club-house-api/archive/main.zip
```

## Usage

First fill in the module Settings with your data

```python
from gpswe.config.settings import settings as gpswe_settings

#The port on which the server will be started
gpswe_settings.PORT = 10500
#The host on which the server will be started
gpswe_settings.HOST = "0.0.0.0"
#Supported version of WialonIPS
gpswe_settings.WIALON_PROTOCOL_VERSION = "2.0"
#Host where the database is deployed
gpswe_settings.POSTGRES_HOST = "0.0.0.0"
#The port on which the database is deployed
gpswe_settings.POSTGRES_PORT = 5432
#The name of the database itself
gpswe_settings.POSTGRES_DB = "gpswe"
#The user's name to connect to the database
gpswe_settings.POSTGRES_USER = "test_user"
#The user's password to connect to the database
gpswe_settings.POSTGRES_PASSWORD = "123"
```

Next, you need to "initialize" your database (create all the necessary libraries in it)

```python
from gpswe.gps_server import init_db

init_db()
```

OK, now you can start the server

```python
from gpswe.gps_server import start_server

start_server()
```

To get extended information about your data, you need to use the method **get_coordinates (imei, 
from_datetime, to_datetime)**, where **"imei"** is the id of your tracker from which the data comes, 
**"from_datetime"** and **"to_datetime"** are the time interval in which you want to receive the data

```python
import datetime
from gpswe.gps_server import get_coordinates

data = get_coordinates(
    imei="1231233123", 
    from_datetime=datetime.datetime(2022, 5, 15), 
    to_datetime=datetime.datetime(2024, 5, 25)
)
```

The data comes in json format

```json
{
  "speed": 20.0, 
  "distance": 248.4, 
  "coordinates": [
    {
      "latitude": 61.2296333, 
      "longitude": 50.8259626
    }, 
    {
      "latitude": 63.4578954564, 
      "longitude": 50.87545689874458
    }
  ]
}
```

speed - average speed over a period of time\
distance - distance traveled\
coordinates - coordinates with latitude and longitude

### All messages will be written to the console via the standard logging python library

## Contributing

Bug reports and/or pull requests are welcome


## License

The module is available as open source under the terms of the [The MIT License (MIT)](https://opensource.org/license/mit/)

