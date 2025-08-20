import unittest
from utils.decorators import integration_test, profiles
from arcgis.features import FeatureSet
from arcgis.geometry import Envelope, Geometry
from arcgis.geometry.filters import intersects
from arcgis.gis import GIS


@profiles.agol
@integration_test
class TestQueryLivingAtlasFeatureLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.item_id = '0ec8512ad21e4bb987d7e848d14e7e24'

    def test_query(self):
        item = self.gis.content.get(self.item_id)
        layers = item.layers
        assert layers, "No layers found in the item."
        layer = layers[0]
        assert layer, "Layer not found in the item."
        query_result = layer.query("FIPS='04005'")
        assert query_result, "Query result is empty."


if __name__ == "__main__":
    unittest.main()
