#!/usr/bin/python

# cronbook.py 
# Britton Fraley
# 2016-04-10

# ------------------------------------------------------------------------------
# This script provides a logging system for monitoring-oriented command line 
# programs.
# ------------------------------------------------------------------------------

# dependencies
from collections import OrderedDict
import argparse
import csv
from datetime import datetime
import json
import os
import sys
import time
import traceback
import urllib2

# globals
g_file_delimiter = '|'
g_file_escapechar = '\\'
g_file_escapechars = OrderedDict({
    '\b' : '\\b',
    '\e' : '\\e',
    '\f' : '\\f',
    '\n' : '\\n',
    '\r' : '\\r',
    '\t' : '\\t'
})
g_file_extension = ''
g_file_line_terminator = '\n'
g_file_quotechar = '"'
g_file_quoting = csv.QUOTE_NONE
g_file_path_root = '/home/mylogin/log/'
g_file_temporary = '/home/mylogin/log/tmp'
g_http_proxies = {}
g_http_url_add = '/cronbook_add'
g_key_name_timestamp = 'timestamp'
g_key_name_unixtime = 'unixtime'
g_rotate = True
g_rotate_max = 10
g_rotate_size = 1048576

# exception classes
class Error(Exception):
    """Base class for exceptions"""
    pass

class BadDatasetError(Error):
    """Error for unrecognized data set"""

    def __init__(self, dataset):
        self.stack_trace = ""
        self.expression = dataset
        self.description = 'dataset \'' + self.expression + '\' invalid'

class BadJsonError(Error):
    """Error for malformed JSON document string"""

    def __init__(self, json):
        self.stack_trace = ""
        self.expression = json
        self.description = 'json invalid'

class BadKeysError(Error):
    """Error for incorrect keys"""

    def __init__(self, keys):
        self.stack_trace = ""
        self.expression = keys
        self.description = 'keys \'' + self.expression + '\' invalid'

class BadQueryError(Error):
    """Error for malformed query parameters"""

    def __init__(self, dataset, time_min, time_max):
        self.stack_trace = ""
        self.expression = dataset + ' from ' + str(time_min) + ' to ' + str(time_max)
        self.description = 'query \'' + self.expression + '\' invalid'

class DiskError(Error):
    """Error for storage i/o"""

    def __init__(self, fname):
        self.stack_trace = traceback.format_exc()
        self.expression = fname
        self.description = 'file open or permission error on \'' + self.expression + '\''

class NetworkError(Error):
    """Error for network i/o"""

    def __init__(self, url):
        self.stack_trace = traceback.format_exc()
        self.expression = url
        self.description = 'network error on \'' + self.expression + '\''

class UploadError(Error):
    """Error for upload"""

    def __init__(self, response):
        self.stack_trace = traceback.format_exc()
        self.expression = response
        self.description = 'upload error while communicating with server, error \'' + self.expression + '\''


# Dataset oriented functions

def ds_create ( f, schema ):
    """Creates a new data set"""
    
    try:
        f.seek(0)
        w = csv.writer(f, delimiter=g_file_delimiter, escapechar=g_file_escapechar, lineterminator=g_file_line_terminator, quoting=g_file_quoting, quotechar=g_file_quotechar)
        w.writerow(schema)
    except:
        raise DiskError(f.name)
    return

def ds_delete ( fname ):
    """Deletes a data set"""
   
    try:
        os.remove(fname)
    except:
        raise DiskError(fname)
    return

def ds_exists ( fname ):
    """Returns boolean for existence of data set"""
   
    try:
        t = os.path.isfile(fname)
    except:
        raise DiskError(fname)
    return t

def ds_filename ( name ):
    """Returns file system representation of data set"""
    
    fname = g_file_path_root + name + g_file_extension
    return fname
   
def ds_query ( f, name, begin, end, return_timestamp ):
    """Returns a JSON document based on query parameters.  Parameters are assumed to be correct"""

    result = []
    schema = ds_schema_read(f)
    #make no assumptions about where file pointer is
    f.seek(0)
    try:
        r = csv.reader(f, delimiter=g_file_delimiter, escapechar=g_file_escapechar, lineterminator=g_file_line_terminator, quoting=g_file_quoting, quotechar=g_file_quotechar)
        first_row_skipped = False
        for row in r:
            if first_row_skipped:
                #unixtime is assumed to be key 1
                unixtime = long(row[0])
                if (begin <= unixtime <= end):
                    if not return_timestamp:
                        #timestamp is assumed to be key 2
                        del row[1]
                    result.append(row)
            else:
                first_row_skipped = True
    except:
        raise DiskError(f.name)
    if not return_timestamp:
        #timestamp hard-coded to field no 2
        del schema[1]
    keys = ""
    i = 0
    for x in schema:
        i += 1
        keys = keys + "\"" + x + "\""
        if (i < len(schema)):
            keys = keys + ", "
    output = "{"
    output = output + " \"dataset\": \"" + name + "\"," 
    output = output + " \"keys\": [" + keys + "]," 
    output = output + " \"values\": " 
    output = output + "[ " 
    i = 0
    for x in result:
        i += 1
        output = output + json.dumps(x) 
        if (i < len(result)):
            output = output + ", "
    output = output + " ]" 
    output = output + " }"
    return i, output

def ds_rename ( fname_from, fname_to ):
    """Renames a data set"""
    
    try:
        os.rename(fname_from, fname_to)
    except:
        raise DiskError(fname_from + " " + fname_to)
    return

def ds_rotate ( name ):
    """Rotates data set files to manage maximum file size"""
   
    try:
        fname = ds_filename(name)
        t = os.path.getsize(fname)
        if (t >= g_rotate_size):
            # preserve existing schema
            f = open(fname, 'r')
            schema = ds_schema_read(f)
            f.close

            # rotate files fro max to 1 to original
            for i in range(g_rotate_max, -1, -1):
                fname_to = fname + '.' + str(i)
                if (i == g_rotate_max):
                    fname_delete = fname + '.' + str(i)
                    if os.path.isfile(fname_delete):
                        os.remove(fname_delete)
                elif (i == 0):
                    fname_from = fname 
                    fname_to = fname + '.' + str(i+1)
                    if os.path.isfile(fname_from):
                        os.rename(fname_from, fname_to)
                else:
                    fname_from = fname + '.' + str(i)
                    fname_to = fname + '.' + str(i+1)
                    if os.path.isfile(fname_from):
                        os.rename(fname_from, fname_to)

            # write new empty file
            f = open(fname, 'w')
            ds_create(f, schema)
            f.close
    except:
        raise DiskError(fname)
    return t

def ds_row_write ( f, row ):
    """Writes a list to data set"""

    # assume that : setbase exists, row contains the correct number of columms, row is ordered to current schema
    row_new = util_values_clean(row)
    try:
        w = csv.writer(f, delimiter=g_file_delimiter, escapechar=g_file_escapechar, lineterminator=g_file_line_terminator, quoting=g_file_quoting, quotechar=g_file_quotechar)
        w.writerow(row_new)
    except:
        raise DiskError(f.name)
    return

def ds_schema_modify ( f, new_keys ):
    """Appends to the schema of a data set"""
  
    try:
        total_new_keys = len(new_keys)
    
        # copy content of existing ds to temporary ds while adding new keys to schema and empty data for those keys
        f.seek(0)
        r = csv.reader(f, delimiter=g_file_delimiter, escapechar=g_file_escapechar, lineterminator=g_file_line_terminator, quoting=g_file_quoting, quotechar=g_file_quotechar)
        t = open(g_file_temporary, 'w')
        w = csv.writer(t, delimiter=g_file_delimiter, quoting=g_file_quoting, quotechar=g_file_quotechar)
        first_row = True
        for row in r:
            if not first_row:
                for x in range(1, total_new_keys + 1):
                    row.append('')
            else:
                for i in new_keys:
                    row.append(i)
                first_row = False
            w.writerow(row)
        t.close()
    
        # empty content of current ds
        f.seek(0)
        f.truncate()
       
        # copy content of temporary ds to existing ds
        t = open(g_file_temporary, 'r')
        r2 = csv.reader(t, delimiter=g_file_delimiter, escapechar=g_file_escapechar, lineterminator=g_file_line_terminator, quoting=g_file_quoting, quotechar=g_file_quotechar)
        w2 = csv.writer(f, delimiter=g_file_delimiter, escapechar=g_file_escapechar, lineterminator=g_file_line_terminator, quoting=g_file_quoting, quotechar=g_file_quotechar)
        for row in r2:
            w2.writerow(row)
        t.close()

        os.remove(g_file_temporary)
    except:
        raise DiskError(f.name)
    return

def ds_schema_read ( f ):
    """Returns a list which represents the schema of a dataset"""
  
    try:
        f.seek(0)
        r = csv.reader(f, delimiter=g_file_delimiter, escapechar=g_file_escapechar, lineterminator=g_file_line_terminator, quoting=g_file_quoting, quotechar=g_file_quotechar)
        schema = r.next()
    except:
        raise DiskError(f.name)
    return schema

def ds_write( f, keys, values ):
    """Writes a list to a data set."""
 
    # keys do not have to be ordered, but are assumed to contain time 
    schema = ds_schema_read(f)
    new_keys = util_key_new(schema, keys)
    total_new_keys = len(new_keys)
    if (total_new_keys > 0):
        ds_schema_modify(f, new_keys)
        schema = ds_schema_read(f)
    f.seek(0, 2)
    n = 0
    for row in values:
        ordered_row = util_values_order(schema, keys, row)
        ds_row_write(f, ordered_row)
        n = n + 1
    return n

def util_is_int(s):
    """Returns boolean for validity of integer"""

    try: 
        int(s)
        return True
    except ValueError:
        return False

def util_json_bad ( s_json ):
    """Returns boolean for validity of JSON document"""

    try: 
        t = json.loads(s_json, strict=False)
    except ValueError:
        return True

    try: 
        name = t["dataset"]
        keys = t["keys"]
        values = t["values"]
    except KeyError:
        return True
    except TypeError:
        return True

    if (len(keys) != len(values[0])):
        return True

    if (len(keys) == 0):
        return True
        
    if (len(values[0]) == 0):
        return True

    if (len(name.rstrip()) == 0):
        return True

    return False
  

def util_json_get_value ( s_json, key ):
    """Returns value for supplied key in JSON document"""

    try: 
        t = json.loads(s_json, strict=False)
    except ValueError:
        return ''

    try: 
        value = t[key]
    except KeyError:
        return ''

    return value

def util_key_bad ( keys ):
    """Returns boolean for validity of keys"""
  
    # look for timestamp key
    timestamp_keys = False
    for i in keys:
        if (i == g_key_name_timestamp):
            timestamp_keys = True
    if (timestamp_keys):
        return True

    # look for duplicate keys or timestamp key
    duplicate_keys = False
    unique_keys = []
    for i in keys:
        if i not in unique_keys:
            unique_keys.append(i)
    if (len(unique_keys) < len(keys)):
        duplicate_keys = True
    if (duplicate_keys):
        return True

    # look for empty keys
    empty_keys = False
    for i in keys:
        if (len(i.rstrip()) == 0):
            empty_keys = True
    if (empty_keys):
        return True
    
    return False

def util_key_exists ( keys, key ):
    """Returns boolean for key in list"""
  
    result = False
    for i in keys:
        if (i == key):
            result = True
    return result

def util_key_index ( keys, key ):
    """Returns index for key in list"""
  
    result = -1
    n = 0
    for i in keys:
        if (i == key):
            result = n
        n += 1
    return result

def util_key_new ( schema, keys ):
    """Returns list of keys not in schema"""
    
    new_keys = []
    for i in keys:
        if i not in schema:
            new_keys.append(i)
    return new_keys

def util_keys_values_add_time ( keys, values ):
    """Modify keys and values so that unixtime, timestamp exist"""

    unixtime = util_timestamp_unix()
    if util_key_exists(keys, g_key_name_unixtime):
        t = util_key_index(keys, g_key_name_unixtime)
        del keys[t]
        keys[:0] = [g_key_name_unixtime, g_key_name_timestamp]
        for x in values:
            values_unixtime = x[t]
            timestamp = util_timestamp_format(values_unixtime)
            del x[t]
            x[:0] = [values_unixtime, timestamp]
    else:
        keys[:0] = [g_key_name_unixtime, g_key_name_timestamp]
        timestamp = util_timestamp_format(unixtime)
        for x in values:
            x[:0] = [unixtime, timestamp]
    return
  
def util_timestamp ( ):
    """Return a timestamp string"""
 
    # return as YYYYY-MM-DD HH:MM:SS.MMMMMM
    ct = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + ' ' + time.strftime('%Z')
    return ct

def util_timestamp_format ( unixtime ):
    """Returns as string a human-readable time stamp from unix time in microseconds"""
   
    # return as YYYY-MM-DD HH:MM:SS.MMMMMM
    t = float(unixtime) / 1000000
    t2 = datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S.%f') + ' ' + time.strftime('%Z')
    return t2

def util_timestamp_unix ( ):
    """Returns as string the current time as unix time in microseconds"""
    
    # not using (datetime.datetime.now - epoch) due to timezone issues
    # don't use float so as to avoid scientific notation
    t = long(time.time() * 1000000)
    t2 = str(t)
    return t2

def util_values_clean ( values ):
    """Returns an escaped list of strings that are valid utf-8"""
  
    new_values = []
    for i in values:
        for j, k in g_file_escapechars.items():
            i = i.replace(j, k)
        i = i.decode('utf-8','ignore').encode("utf-8")
        new_values.append(i)
    return new_values

def util_values_order ( schema, keys, values ):
    """Returns a list ordered to the schema"""
    
    new_values = []
    for i in schema:
        found_key = False
        for j in keys:
            if i == j:
                item = values[keys.index(j)]
                found_key = True
        if found_key:
            new_values.append(item)
        else:
            new_values.append('')
    return new_values


# high-level functions

def add ( data ):
    """Process JSON string to add to data set"""
    
    if util_json_bad(data):
        raise BadJsonError(data)
        return

    t = json.loads(data, strict=False)
    name = t["dataset"]
    keys = t["keys"]
    values = t["values"]

    if util_key_bad(keys):
        raise BadKeysError(str(keys))
        return

    util_keys_values_add_time(keys, values)

    try:
        fname = ds_filename(name)
        new_dataset = not(ds_exists(fname))
        if new_dataset:
            f = open(fname, 'w') 
            ds_create(f, keys)
            f.close()
        f = open(fname, 'r+') 
        n = ds_write(f, keys, values)
        f.close()
        if g_rotate:
            ds_rotate(name)
    except Exception as e:
        raise DiskError(fname)
    return n, name

def delete ( name ):
    """Removes a data set"""

    fname = ds_filename(name)
    if not ds_exists(fname):
        raise BadDatasetError(name)
        return

    ds_delete(fname)
    return
    
def query ( name, time_min, time_max ):
    """Return a JSON document based on values matching query parameters"""

    if not (util_is_int(time_min) and util_is_int(time_max)):
        raise BadQueryError(name, time_min, time_max)
        return
    if ((time_min < 0) or (time_max < 0) or (time_max < time_min)):
        raise BadQueryError(name, time_min, time_max)
        return
    fname = ds_filename(name)
    if not ds_exists(fname):
        raise BadDatasetError(name)
        return

    try:
        f = open(fname, 'r') 
        n, output = ds_query(f, name, long(time_min), long(time_max), True)
        f.close()
    except Exception as e:
        raise DiskError(fname)
    return n, output

def rename ( name_from, name_to ):
    """Renames a data set"""
    
    fname_from = ds_filename(name_from)
    fname_to = ds_filename(name_to)
    if not ds_exists(fname_from):
        raise BadDatasetError(name_from)
        return
    if ds_exists(fname_to):
        raise BadDatasetError(name_to)
        return

    ds_rename(fname_from, fname_to)
    return
    
def upload ( name, time_min, time_max, host, port ):
    """Uploads the content of a query to a remote node"""

    if not (util_is_int(time_min) and util_is_int(time_max)):
        raise BadQueryError(name, time_min, time_max)
        return
    if ((time_min < 0) or (time_max < 0) or (time_max < time_min)):
        raise BadQueryError(name, time_min, time_max)
        return
    fname = ds_filename(name)
    if not ds_exists(fname):
        raise BadDatasetError(name)
        return

    f = open(fname, 'r') 
    n, data = ds_query(f, name, long(time_min), long(time_max), False)
    f.close()

    if (n > 0):
        url = 'http://' + host + ':' + port + g_http_url_add
        proxy_handler = urllib2.ProxyHandler(g_http_proxies)
        opener = urllib2.build_opener(proxy_handler)
        header = {}
        header['Content-Type'] = 'application/json'
        request = urllib2.Request(url, data, header)
        request.get_method = lambda: 'PUT'
        try:
            f = opener.open(request)
            response = f.read()
            f.close()
        except:
            raise NetworkError(url)
    return n

    
# main starts here...

def util_error ( f, location, message ):
    """Write a short error message"""

    t = util_timestamp() + ', ' + location + ': ' + message + '\n'
    f.write(t)
    return

def util_success ( f, location, message ):
    """Write a short success message"""

    t = util_timestamp() + ', ' + location + ': ' + message + '\n'
    f.write(t)
    return

if __name__ == '__main__':

    # define command line argument parser
    d = 'Cronbook. Time series data processor. JSON format is {"dataset":"name", "keys":["key_1","key_n"], "values":[["value_1","value_n"]]}'
    parser = argparse.ArgumentParser(description = d)
    parser.add_argument('-a', '--add', nargs=1, help='add via inline JSON string', metavar=('JSON'))
    parser.add_argument('-d', '--delete', nargs=1, help='delete dataset', metavar=('NAME'))
    parser.add_argument('-f', '--file', nargs=1, help='add via JSON file', metavar=('FILE'))
    parser.add_argument('-l', '--logfile', nargs=1, help='write output to file', metavar=('FILE'))
    parser.add_argument('-q', '--query', nargs=3, help='query dataset', metavar=('NAME', 'MIN', 'MAX'))
    parser.add_argument('-r', '--rename', nargs=2, help='rename dataset', metavar=('NAME_FROM', 'NAME_TO'))
    parser.add_argument('-u', '--upload', nargs=5, help='upload dataset', metavar=('NAME', 'MIN', 'MAX', 'HOST', 'PORT'))
    parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')
    args = parser.parse_args()

    if args.logfile:
        function = 'logfile'
        try:
            f_success = f_error = open(args.logfile[0], 'a')
        except:
            t = 'file open or permission error on \'' + args.logfile[0] + '\''
            util_error(sys.stderr, function, t)
            sys.exit(1)
    else:
        f_success = sys.stdout
        f_error = sys.stderr

    if args.add:
        function = 'add'
        try:
            n, dataset = add(args.add[0])
            if args.verbose:
                t = str(n) + ' sets added to dataset ' + dataset
                util_success(f_success, function, t)
        except Error as e: 
            util_error(f_error, function, e.description)
            sys.exit(1)
        sys.exit(0)

    if args.delete:
        function = 'delete'
        try:
            delete(args.delete[0])
            if args.verbose:
                t = 'dataset ' + args.delete[0] + ' deleted'
                util_success(f_success, function, t)
        except Error as e: 
            util_error(f_error, function, e.description)
            sys.exit(1)
        sys.exit(0)

    if args.file:
        function = 'add file'
        try:
            f = open(args.file[0], 'r')
            content = f.read()
            f.close()
        except:
            t = 'file open or permission error on \'' + args.file[0] + '\''
            util_error(f_error, function, t)
            sys.exit(1)

        try:
            n, dataset = add(content)
            if args.verbose:
                t = str(n) + ' sets added to dataset ' + dataset
                util_success(f_success, function, t)
        except Error as e: 
            util_error(f_error, function, e.description)
            sys.exit(1)
        sys.exit(0)

    if args.query:
        function = 'query'
        try:
            n, output = query(args.query[0], args.query[1], args.query[2])
            if args.verbose:
                t = str(n) + ' sets returned via query ' + args.query[0] + ' from ' + args.query[1] + ' to ' + args.query[2] 
                util_success(f_success, function, t)
            if (n > 0):
                print output
        except Error as e: 
            util_error(f_error, function, e.description)
            sys.exit(1)
        sys.exit(0)

    if args.rename:
        function = 'rename'
        try:
            rename(args.rename[0], args.rename[1])
            if args.verbose:
                t = 'dataset ' + args.rename[0] + ' renamed to ' + args.rename[1]
                util_success(f_success, function, t)
        except Error as e: 
            util_error(f_error, function, e.description)
            sys.exit(1)
        sys.exit(0)

    if args.upload:
        function = 'upload'
        try:
            n = upload(args.upload[0], args.upload[1], args.upload[2], args.upload[3], args.upload[4])
            if args.verbose:
                t = str(n) + ' sets uploaded via query ' + args.upload[0] + ' from ' + args.upload[1] + ' to ' + args.upload[2] + ' to server ' + args.upload[3] + ' on port ' + args.upload[4]
                util_success(f_success, function, t)
        except Error as e: 
            util_error(f_error, function, e.description)
            sys.exit(1)
        sys.exit(0)

    sys.exit(0)
