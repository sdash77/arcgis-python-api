from utils._common import *

def test_arcgis_being_imported_correctly():
    import arcgis
    assert arcgis.__file__ == os.path.join(GEOSAURUS_SRC_ARCGIS_DIR,
                                           "__init__.py")

