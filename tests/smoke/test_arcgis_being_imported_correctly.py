# Test that the imported arcgis API is the one from ../../src
import unittest

from utils._common import *
from utils.imports import *


class TestArcgisBeingImportedCorrectly(unittest.TestCase):

    def test_arcgis_being_imported_is_dev(self):
        clear_arcgis_import_cache()
        import arcgis

        expected = os.path.join(GEOSAURUS_SRC_ARCGIS_DIR, "__init__.py").lower()
        actual = arcgis.__file__.lower()
        assert actual == expected
        clear_arcgis_import_cache()

    # Test that each module can be imported without SyntaxError (basic sanity)
    # This type of import syntax (from foo import *) must be run in module level

    clear_arcgis_import_cache()
    import arcgis

    clear_arcgis_import_cache()

    def test_all_arcgis_submodule_imports(self):
        """Test individual imports inside of test itself"""
        import_all_arcgis_submodules()


if __name__ == "__main__":

    unittest.main()
