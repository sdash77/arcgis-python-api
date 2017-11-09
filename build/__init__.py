import os
import shutil
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

class empty_temp_folder:
    """Use with "with" syntax like "with empty_temp_folder() as tmp:"
    Creates a temporary folder and deletes it after finished being used"""
    def __enter__(self):
        self.temp_folder = os.path.join(gettempdir(),
                                   ".{}".format(hash(os.times())))
        os.makedirs(self.temp_folder)
        return self.temp_folder

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.temp_folder)

DEFAULT_META_YML_FILE = os.path.abspath(os.path.join(
    BUILD_DIR,
    "meta",
    "default_meta.yaml"))

ACTIVE_META_YML_FILE = os.path.abspath(os.path.join(
    BUILD_DIR,
    "arcgis",
    "meta.yaml"))

SUPPORTED_WIN = ['win-32', 'win-64']
SUPPORTED_LINUX = ['linux-32', 'linux-64']
SUPPORTED_OSX = ['osx-64']

SUPPORTED_OSES = SUPPORTED_WIN +\
                 SUPPORTED_LINUX +\
                 SUPPORTED_OSX
DEFAULT_OSES = SUPPORTED_OSES

SUPPORTED_PYS = ['3.5', '3.6']
DEFAULT_PYS = SUPPORTED_PYS

def is_windows(os_build_target):
    return os_build_target in SUPPORTED_WIN

def is_unix(os_build_target):
    return (os_build_target in SUPPORTED_LINUX) or\
           (os_build_target in SUPPORTED_OSX)

def is_py_35(python_version):
    return python_version == SUPPORTED_PYS[0]

def is_py_36(python_version):
    return python_version == SUPPORTED_PYS[1]
