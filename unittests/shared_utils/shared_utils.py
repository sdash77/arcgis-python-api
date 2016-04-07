"""

Module for broadly useful functionality to most tests/teams.

Created 2010, Modified April 2016.
Originally from PyUnit harness

"""

import platform
import sys
import os
import shutil
import re
import base64
import locale
import xml.etree.ElementTree as ET
import imp

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

try:
    unicode
except NameError:  # Python 3
    unicode = str

# variable for all to use when branching for py2 v py3
PY3 = True if sys.version[0] > '2' else False
PY2 = True if sys.version[0] < '3' else False

# Read unittest.ini, ../unittest.ini, ../../unittest.ini etc
# Variables in the unittest.ini lower down in the dir structure win
conf = ConfigParser.ConfigParser()
paths = [os.getcwd()]
while os.path.dirname(paths[-1]) not in (os.path.dirname(__file__), paths[-1]):
    paths.append(os.path.dirname(paths[-1]))

# if test imported from outside QATest/pyunit directory
# find the top level unittest.ini, which is located in the current directory
if not os.path.dirname(__file__) in paths:
    paths.append(os.path.dirname(os.path.dirname(__file__)))

conf.read(reversed([os.path.join(p, 'unittest.ini') for p in paths]))

last_modified_ini = 0
for f in [os.path.join(p, 'unittest.ini') for p in paths]:
    if os.path.isfile(f):
        mod = os.stat(f).st_mtime
        last_modified_ini = mod if mod > last_modified_ini else last_modified_ini

### get server infos  ///
def get_server_info(config_file, section="arcgiscom"):
    '''Returns a dict containing the info about the server for the given domain. '''
    
    srvProps = ConfigParser.ConfigParser()
    srvProps.read(config_file)
    server_info = {}
    server_info["url"] = srvProps.get(section, 'url')            
    server_info["admin_user"] = srvProps.get(section, 'admin_user')            
    server_info["admin_pass"] = srvProps.get(section, 'admin_pass')                            
    
    return server_info

### /// get server infos




class _AssertRaisesContext(object):
    """A context manager used to implement assertRaisesRegexp methods."""

    def __init__(self, expected, expected_regexp=None):
        self.expected = expected
        self.expected_regexp = expected_regexp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)
            raise self.failureException(
                "{0} not raised".format(exc_name))
        if not issubclass(exc_type, self.expected):
            # let unexpected exceptions pass through
            return False
        self.exception = exc_value # store for later retrieval
        if self.expected_regexp is None:
            return True

        expected_regexp = self.expected_regexp
        """if PY2 and isinstance(expected_regexp, (unicode, str)):
            #using python2
            expected_regexp = re.compile(re.sub(r"%\d", ".*", expected_regexp))
        elif PY3 and isinstance(expected_regexp, str):
            #using python3
            expected_regexp = re.compile(re.sub(r"%\d", ".*", expected_regexp))
        else:
            pass"""
        if isinstance(expected_regexp, unicode):
            # replace %1 %2 to .* to match any string

            expected_regexp = re.compile(re.sub(
                r"%\d", ".*", re.sub(r"!\w!", "", expected_regexp)))
        if not expected_regexp.search(unicode(exc_value)):
            raise AssertionError('"%s" does not match "%s"' %
                                 (expected_regexp.pattern, unicode(exc_value)))
        return True

def assertRaisesRegexp(expected_exception, expected_regexp,
                       callable_obj=None, *args, **kwargs):
    """ similar to unittest.TestCase.assertRaisesRegexp, but
    this function can handle exceptions with unicode messages """
    context = _AssertRaisesContext(expected_exception,
                                   expected_regexp)
    if callable_obj is None:
        return context
    with context:
        callable_obj(*args, **kwargs)


def assertRaisesMsgID(expected_exception, expected_msg_id, callable_obj=None,
                      *args, **kwargs):
    """ similar to unittest.TestCase.assertRaisesRegexp, but
    this function can handle exceptions with error message ids """
    context = _AssertRaisesContext(expected_exception, 'err msg')                                   
                                   #getErrorMsgByID(expected_msg_id))
    if callable_obj is None:
        return context
    with context:
        callable_obj(*args, **kwargs)


def create_output_folder(out_name='out_data', unique_method='by_date', del_existing=False):
    """ Routine creates a folder (unique or not) in the same dir as the py module to provide
    a location for Sam to write intermediate or output data.
    """
    if unique_method == 'by_date':
        import datetime
        out_name = out_name + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S")
    elif unique_method == 'by_guid':
        import uuid
        out_name = '{0}_{1}'.format(out_name, (uuid.uuid1()))
    elif unique_method == 'none':
        pass

    output_dir = os.path.dirname(os.path.dirname(os.path.join(os.getcwd(), __file__)))
    output_dir = os.path.join(output_dir, 'out_data', out_name)

    if os.path.exists(output_dir) and del_existing:
        shutil.rmtree(output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return output_dir

class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)
    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__
    def __get__(self, obj, objtype):
        """Support instance methods."""
        import functools
        return functools.partial(self.__call__, obj)

@memoized
def cr_status(cr_number):
    """ Returns a CRs status from the crlookup site"""
    try:
        from urllib.request import urlopen
    except ImportError:
        from urllib import urlopen

    try:
        doc = urlopen(r'http://qamonitor/CrLookupAnon/?cr=' + str(cr_number))
        #https://github.com/ArcGIS/geosaurus/issues
        return re.search(b'(?<="lblCrStatus" class="l5">)[a-zA-Z ]*', doc.read()).group(0)
    except:
        return None

def cr_not_fixed_yet(cr_number):
    """ Returns False if status of CR is not valid"""
    return True if cr_status(cr_number) in [b'New', b'Open', b'In Progress', b'Deferred'] else False


def validate():
    """ test routines in this module """

    print("TESTING shared_utils functions")
    #print("resolve_data_path: " + resolve_data_path('myshps/counties.shp'))
    print("create_output_folder() : " + create_output_folder())

    print("create_output_folder('my_out_folder') : " +
          create_output_folder('my_out_folder'))

    print("create_output_folder('my_out_folder', 'by_date') : " +
          create_output_folder('my_out_folder', 'by_date'))

    print("create_output_folder('my_out_folder', 'by_guid') : " +
          create_output_folder('my_out_folder', 'by_guid'))

    print('cr_status')
    for i in ['168483', 'cr168483', '38691', '38691']:
        print(' {0} : {1}'.format(i, cr_status(i)))
    print('')


    print('unittest.ini')
    for section in ['unittest']:
        print('\n' + section)
        for k, v in conf.items(section):
            print('{:<18}: {}'.format(k, v))

if __name__ == "__main__":
    validate()
