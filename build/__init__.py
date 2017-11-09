import os
from tempfile import gettempdir

GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..'))

BUILD_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "build"))

BUILD_OUTPUT_DIR = os.path.abspath(os.path.join(
    BUILD_DIR,
    "output"))

TEMP_DIR = gettempdir()

DEFAULT_META_YML_FILE = os.path.abspath(os.path.join(
    BUILD_DIR,
    "meta",
    "default_meta.yaml"))

ACTIVE_META_YML_FILE = os.path.abspath(os.path.join(
    BUILD_DIR,
    "arcgis",
    "meta.yaml"))

SUPPORTED_OSES = ['win', 'unix']
SUPPORTED_PYS = ['3.5', '3.6']
DEFAULT_PY = '3.6'
DEFAULT_OS = os.name

PY36_REGEX = ".*3\.?6.*" #if '36' or '3.6' in string
PY35_REGEX = ".*3\.?5.*" #if '35' or '3.5' in string
UNIX_REGEX = "".join([
             "(?i).*unix.*", #if 'unix' (case insensitive) in string
             "|.*linux.*",   #OR if 'linux' (case insensitive) in string
             "|.*osx.*",     #OR if 'osx' (case insensitive) in string
             "|.*macos.*",   #OR if 'macos' (case insensitive) in string
             "|.*posix.*"])  #OR if 'posix' (case insensitive) in string
WINDOWS_REGEX = "".join([
                "(?i).*win.*", #if 'win' (case insensitive) in string
                "|.*nt.*"])    #OR if 'nt' (case insensitive) in string
