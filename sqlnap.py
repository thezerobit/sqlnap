# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import collections

import sqlsoup
from sqlalchemy.exc import IntegrityError
from bottle import (response, request, route, run)

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
    response.content_type = 'application/json'
    return json.dumps(obj)

@route('/db', method='GET')
def list_dbs():
    tables = [x[0] for x in DB.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='public'")]
    return dump_json(tables)

@route('/db/:table', method='GET')
def list_rows(table):
    table_obj = DB.entity(table)
    limit = request.query.get("limit", DEFAULT_LIMIT)
    data = [row_to_data(x) for x in table_obj.limit(limit).all()]
    return dump_json(data)

def do_create_row(table_obj, vals):
    try:
        created_row = table_obj.insert(**vals)
        DB.commit()
    except IntegrityError, error:
        DB.rollback()
        request.status = 400
        return unicode(error)
    except:
        DB.rollback()
    request.status = 201
    unicode(created_row) # needs a kick, for some reason
    return dump_json(row_to_data(created_row))

@route('/db/:table', method='POST')
def create_row(table):
    if request.json:
        table_obj = DB.entity(table)
        print request.json
        return do_create_row(table_obj, request.json)
    else:
        request.status = 400
        return "Bad Request"

@route('/db/:table/:pk', method='GET')
def get_by_id(table, pk):
    table_obj = DB.entity(table)
    obj = table_obj.get(pk)
    if obj is None:
        request.status = 404
        return "Not Found"
    data = row_to_data(obj)
    return dump_json(data)

@route('/db/:table/:pk', method=['PATCH', 'PUT'])
def create_or_update(table, pk):
    table_obj = DB.entity(table)
    obj = table_obj.get(pk)
    if obj is None:
        if request.method == 'PATCH':
            request.status = 404
            return "Not Found"
        else:
            keys = table_obj._table.primary_key.columns.keys()
            if len(keys) == 1:
                key = keys[0]
                vals = request.json.copy()
                vals[key] = pk
                return do_create_row(table_obj, vals)
            else:
                request.status = 500
                return "Primary Key Error"
    elif request.json:
        try:
            for key in request.json:
                setattr(obj, key, request.json[key])
            DB.commit()
        except:
            DB.rollback()
            request.status = 500
            return "Database Error"
        request.status = 201
        unicode(obj) # kick it!
        data = row_to_data(obj)
        return dump_json(data)
    else:
        request.status = 400
        return "Bad Request"

if __name__=='__main__':
    run(host='localhost', port='8080')
