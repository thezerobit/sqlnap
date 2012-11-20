# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import collections

import sqlsoup
import bottle

DBURL = 'postgresql+psycopg2://testuser:testpass@localhost/test'
DB = sqlsoup.SQLSoup(DBURL)
DEFAULT_LIMIT=1000
DEFAULT_ENCODING='utf-8'
IDENTITY_TYPES = (unicode, int, float, bool)

def to_data(obj):
    for thetype in IDENTITY_TYPES:
        if isinstance(obj, thetype):
            return obj
    if obj is None:
        return obj
    elif isinstance(obj, str):
        return obj.decode(DEFAULT_ENCODING)
    elif isinstance(obj, collections.Mapping):
        return dict([(unicode(key), to_data(obj[key])) for key in obj])
    elif isinstance(obj, collections.Sequence):
        return [to_data(val) for val in obj]
    else:
        return unicode(obj)

def row_to_data(obj):
    return dict([(key, to_data(obj.__dict__[key])) \
            for key in obj.__dict__ if isinstance(key, unicode)])

def dump_json(obj):
    bottle.response.content_type = 'application/json'
    return json.dumps(obj)

@bottle.route('/db', method='GET')
def list_dbs():
    tables = [x[0] for x in DB.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='public'")]
    return dump_json(tables)

@bottle.route('/db/:table', method='GET')
def list_rows(table):
    table_obj = DB.entity(table)
    limit = bottle.request.query.get("limit", DEFAULT_LIMIT)
    data = [row_to_data(x) for x in table_obj.limit(limit).all()]
    return dump_json(data)

@bottle.route('/db/:table', method='POST')
def create_row(table):
    if bottle.request.json:
        table_obj = DB.entity(table)
        created_row = table_obj.insert(**bottle.request.json)
        DB.commit()
        bottle.request.status = 201
        unicode(created_row) # needs a kick, for some reason
        return dump_json(row_to_data(created_row))
    else:
        bottle.request.status = 400
        return "Bad Request"

@bottle.route('/db/:table/:pk', method='GET')
def get_by_id(table, pk):
    table_obj = DB.entity(table)
    obj = table_obj.get(pk)
    data = row_to_data(obj)
    return dump_json(data)

if __name__=='__main__':
    bottle.run(host='localhost', port='8080')
