from utils._common import *

def test_arcgis_being_imported_correctly():
    import arcgis
    expected = os.path.join(GEOSAURUS_SRC_ARCGIS_DIR, "__init__.py").lower()
    actual = arcgis.__file__.lower()
    assert actual == expected
