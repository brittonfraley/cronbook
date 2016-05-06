#!/usr/bin/python

# cronbook_copier.py 
# Britton Fraley
# 2016-04-10

# ------------------------------------------------------------------------------
# This script provides log file copy ability to cronbook.py
# ------------------------------------------------------------------------------

# dependencies
import argparse
import cronbook
import os
import shelve
import sys
import traceback

# globals
g_database = '/home/mylogin/log/cronbook_copier_db'
g_datasets = [
    'dataset_1',
    'dataset_2'
]
g_file_server_log = '/home/mylogin/log/cronbook_copier_log'
g_host = 'localhost'
g_port = '8080'

# exception classes
class Error(Exception):
    """Base class for exceptions"""
    pass

class DiskError(Error):
    """Error for storage i/o"""

    def __init__(self, expression):
        self.stack_trace = traceback.format_exc()
        self.expression = fname
        self.description = 'file open or permission error on \'' + self.expression + '\''

   
def copy ( ):
    """Copy datasets to server"""

    function = 'copy'
    time_current = cronbook.util_timestamp_unix() 
    d = shelve.open(g_database)

    # get last timestamp for each dataset and call upload for last to current timestamp
    for dataset in g_datasets:
        if not d.has_key(dataset):
            time_last = long(0)
            time_min = time_last
        else:
            time_last = long(d[dataset]) 
            time_min = time_last + 1
        n = cronbook.upload(dataset, time_min, time_current, g_host, g_port)
        if (n > 0):
            d[dataset] = time_current
            t = str(n) + ' sets uploaded via query ' + dataset + ' from ' + str(time_min) + ' to ' + str(time_current)  + ' to server ' + g_host + ' on port ' + g_port
            util_success(function, t)

    d.close()
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

if __name__ == '__main__':

    util_success('main', 'copier started')

    # define command line argument parser
    d = 'Cronbook copier.'
    parser = argparse.ArgumentParser(description = d)
    parser.add_argument('-c', '--copy', help='copy datasets', action='store_true')
    args = parser.parse_args()

    if args.copy:
        function = 'copy'
        try:
            copy()
        except cronbook.Error as e: 
            util_error(function, e.description)
            util_success('main', 'copier stopped')
            sys.exit(1)
        except Error as e: 
            util_error(function, e.description)
            util_success('main', 'copier stopped')
            sys.exit(1)

    util_success('main', 'copier stopped')
    sys.exit(0)
