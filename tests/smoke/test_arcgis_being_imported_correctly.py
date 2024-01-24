# Test that the imported arcgis API is the one from ../../src
import unittest

from utils._common import *
from utils.imports import *


class TestArcgisBeingImportedCorrectly(unittest.TestCase):

    def test_arcgis_being_imported_is_dev(self):
        if should_allow_testing_against_packaged():
            self.skipTest("Skipping test_arcgis_being_imported_is_dev because ALLOW_INSTALLED_ARCGIS is set to true")
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
        import_all_arcgis_submodules(import_learn=should_smoketest_arcgis_learn())


if __name__ == "__main__":

    unittest.main()
