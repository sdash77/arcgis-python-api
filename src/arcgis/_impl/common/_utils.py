"""set of common utilities"""
import os
import sys
import time
import uuid
import zipfile
import datetime
import tempfile
from contextlib import contextmanager

import six
import logging 

#----------------------------------------------------------------------
def create_uid():
    if six.PY2:
        return uuid.uuid4().get_hex()
    else:
        return uuid.uuid4().hex
#----------------------------------------------------------------------
def _date_handler(obj):
    if isinstance(obj, datetime.datetime):
        return local_time_to_online(obj)
    else:
        return obj
#----------------------------------------------------------------------
def local_time_to_online(dt=None):
    """
       converts datetime object to a UTC timestamp for AGOL
       Inputs:
          dt - datetime object
       Output:
          Long value
    """
    if dt is None:
        dt = datetime.datetime.now()

    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset =  (time.altzone if is_dst else time.timezone)

    return int((time.mktime(dt.timetuple())  * 1000) + (utc_offset *1000))
#----------------------------------------------------------------------
def online_time_to_string(value,timeFormat):
    """
       Converts a timestamp to date/time string
       Inputs:
          value - timestamp as long
          timeFormat - output date/time format
       Output:
          string
    """
    return datetime.datetime.fromtimestamp(value /1000).strftime(timeFormat)
#----------------------------------------------------------------------
def timestamp_to_datetime(timestamp):
    """
       Converts a timestamp to a datetime object
       Inputs:
          timestamp - timestamp value as Long
       output:
          datetime object
    """
    return datetime.datetime.fromtimestamp(timestamp /1000)

###########################################################################
class Error(Exception): pass
#--------------------------------------------------------------------------
@contextmanager
def _tempinput(data):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write((bytes(data, 'UTF-8')))
    temp.close()
    yield temp.name
    os.unlink(temp.name)
#--------------------------------------------------------------------------
def _lazy_property(fn):
    '''Decorator that makes a property lazy-evaluated.
    '''
    # http://stevenloria.com/lazy-evaluated-properties-in-python/
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property
#--------------------------------------------------------------------------
def _is_shapefile(data):
    if zipfile.is_zipfile(data):
        zf = zipfile.ZipFile(data, 'r')
        namelist = zf.namelist()
        for name in namelist:
            if name.endswith('.shp') or name.endswith('.SHP'):
                return True
    return False
#--------------------------------------------------------------------------
def rot13(s):
    result = ""

    # Loop over characters.
    for v in s:
        # Convert to number with ord.
        c = ord(v)

        # Shift number back or forward.
        if c >= ord('a') and c <= ord('z'):
            if c > ord('m'):
                c -= 13
            else:
                c += 13
        elif c >= ord('A') and c <= ord('Z'):
            if c > ord('M'):
                c -= 13
            else:
                c += 13

        # Append to result.
        result += chr(c)

    # Return transformation.
    return result
#--------------------------------------------------------------------------
def _to_utf8(data):
    """ Converts strings and collections of strings from unicode to utf-8. """
    if isinstance(data, dict):
        return {_to_utf8(key): _to_utf8(value) \
                for key, value in data.items() if value is not None}
    elif isinstance(data, list):
        return [_to_utf8(element) for element in data]
    elif isinstance(data, str):
        return data
    elif isinstance(data, six.text_type):
        return data.encode('utf-8')
    elif isinstance(data, (float, six.integer_types)):
        return data
    else:
        return data
#--------------------------------------------------------------------------
class _DisableLogger():
    def __enter__(self):
       logging.disable(logging.CRITICAL)
    def __exit__(self, a, b, c):
       logging.disable(logging.NOTSET)
