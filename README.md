# SQLNAP

Simple RESTful HTTP interface for a PostgreSQL database built with SQLSoup
and Bottle.py.

## REST / HTTP interface

All endpoints return JSON.

''' /db '''
Provides a list of tables.

''' /db/:tablename '''
Provides a list of rows (as dictionaries) from table. Accepts `limit` query
parameter which defaults to 1000.

''' /db/:tablename/:pk '''
Retrieves a single row as dictionary based on primary key.

## Install

Ubuntu:

```
sudo apt-get install postgresql postgresql-server-dev-9.1 python-dev

edit DBURL in sqlnap.py to point to your database

# create and activate a virtualenv
pip install -r requirements.txt
python sqlnap.py # to run test server at http://localhost:8080/
```

## Deployment

See Bottle's documentation on
[Deployment](http://bottlepy.org/docs/stable/deployment.html).

## Author

* Stephen A. Goss (steveth45@gmail.com)

## Copyright

Copyright (c) 2012 Stephen A. Goss (steveth45@gmail.com)

# License

Licensed under the Modified BSD License.

