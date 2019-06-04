import sys

from utils._common import *

def pytest_configure(config):
    sys.path.insert(0, os.path.join(GEOSAURUS_ROOT_DIR, "src"))
    import arcgis
    assert arcgis.__file__ == os.path.join(GEOSAURUS_SRC_ARCGIS_DIR,
                                           "__init__.py")

