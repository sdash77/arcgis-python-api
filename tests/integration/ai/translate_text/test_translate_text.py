import unittest
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

from arcgis.ai import translate

enable_verbose_logging()

@profiles.agol
@integration_test
class TestFeatureLayerCollectionSwap(unittest.TestCase):
    """Tests the translate text logic"""
    
    def test_translate(self):
        result = translate(
            text=['cat', 'dog', 'fish'],
            to_language=['fr'],
            from_language="en-us")
        assert isinstance(result, dict)

if __name__ == "__main__":
    unittest.main()
