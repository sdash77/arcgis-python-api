"""
contains commonly used tools
"""
import os
import tempfile
import zipfile
from contextlib import contextmanager
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

def _to_utf8(data):
    """ Converts strings and collections of strings from unicode to utf-8. """
    if isinstance(data, dict):
        return {_to_utf8(key): _to_utf8(value) \
                for key, value in data.items()}
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
