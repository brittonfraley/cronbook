#!/usr/bin/python

# cronbook_server.py 
# Britton Fraley
# 2016-04-10

# ------------------------------------------------------------------------------
# This script provides a rest interface to cronbook.py
# ------------------------------------------------------------------------------

# dependencies
from bottle import route, run, request, abort
import cronbook
import json
import os
import sys

# globals
g_file_server_log = '/home/mylogin/log/cronbook_server_log'
g_file_server_pid = '/home/mylogin/log/cronbook_server_pid'
g_host = 'localhost'
g_port = 8080
g_url_add = '/cronbook_add'
g_url_query = '/cronbook_query'

@route(g_url_add, method='PUT')
def put_cronbook_add():
    """Process JSON string to add to data set"""

    function = 'add'
    arg_json = request.body.readline()
    if not arg_json:
        t = 'no data received'
        util_error(function, t)
        abort(400, t)
    try:
        n, dataset = cronbook.add(arg_json)
        t = str(n) + ' sets added to dataset ' + dataset 
        util_success(function, t)
    except cronbook.Error as e: 
        util_error(function, e.description)
        abort(400, e.description)
    except:
        t = 'error' 
        util_error(function, t)
        abort(400, t)
    return

@route(g_url_query, method='GET')
def get_cronbook_query():
    """Return a JSON document based on values matching query parameters"""
   
    function = 'query'
    try:
        n, output = cronbook.query(request.query.dataset, long(request.query.time_min), long(request.query.time_max))
        t = str(n) + ' sets returned via query ' + request.query.dataset + ' from ' + request.query.time_min + ' to ' + request.query.time_max 
        util_success(function, t)
        if (n == 0):
            abort(404, 'no results')
        return output
    except ValueError:
        t = 'invalid query'
        util_error(function, t)
        abort(400, t)
    except cronbook.Error as e: 
        util_error(function, e.description)
        abort(400, e.description)
    except:
        t = 'error' 
        util_error(function, t)
        abort(400, t)
    return

def util_error ( location, message ):
    """Write a short error message"""

    t = cronbook.util_timestamp() + ', ' + location + ': ' + message + '\n'
    f = open(g_file_server_log, 'a')
    f.write(t)
    f.close()
    return

def util_success ( location, message ):
    """Write a short success message"""

    t = cronbook.util_timestamp() + ', ' + location + ': ' + message + '\n'
    f = open(g_file_server_log, 'a')
    f.write(t)
    f.close()
    return


# pre-server init
function = 'main'
pid = str(os.getpid())
f = open(g_file_server_pid, 'w')
f.write(pid)
f.close()
util_success(function, 'server started as pid ' + pid)

# server init
run(host=g_host, port=g_port, quiet=True)

# post-server init
os.remove(g_file_server_pid)
util_success(function, 'server stopped')
sys.exit(0)
