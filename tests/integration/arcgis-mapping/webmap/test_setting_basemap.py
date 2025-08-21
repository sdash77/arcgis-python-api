import sys
sys.path.insert(0, r"C:\workspace\geosaurus\tests")
import time
import unittest
from arcgis.map import Map
from arcgis.features import FeatureLayer
from arcgis.layers import VectorTileLayer
from utils.decorators import integration_test, profiles


@profiles.all
@integration_test
class TestAddLayersToMap(unittest.TestCase):

    def setUp(self):
        # create webmap
        self.wm = Map(gis=self.gis)
        assert isinstance(self.wm, Map)

    def test_vector_layer(self):
        """Test adding a vector tile layer as a basemap"""

        # add layer
        layer = VectorTileLayer(
            "https://basemaps.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer",
            gis=self.gis,
        )
        assert isinstance(layer, VectorTileLayer)

        self.wm.basemap.basemap = layer
        assert (
            self.wm.basemap.basemap["baseMapLayers"][0]["layerType"]
            == "VectorTileLayer"
        )
        self.wm.basemap.title = self.wm.basemap.basemap["baseMapLayers"][0]["title"]
        assert self.wm.basemap.basemap["title"] == layer.properties.name.replace(
            "_", " "
        )

    def test_basemaps_list(self):
        """Test adding each basemap in basemaps property as a basemap."""

        basemaps = self.wm.basemap.basemaps

        for basemap in basemaps:
            self.wm.basemap.basemap = basemap
            assert basemap.replace("-", " ").lower() in self.wm.basemap.basemap["title"].lower()
            time.sleep(2)

    def test_invalid_basemap(self):
        """Test adding each basemap that isn't valid type."""

        layer = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        try:
            self.wm.basemap.basemap = layer
            assert 1 == 2
        except Exception:
            # This should fail so it should end here
            assert 1 == 1

    def test_different_sr(self):
        """Test adding a basemap with a different spatial reference than original."""
        current_map_sr = self.wm.extent["spatialReference"]["wkid"]
        new_basemap = VectorTileLayer(
            "https://basemaps.arcgis.com/arcgis/rest/services/OpenStreetMap_GCS_v2/VectorTileServer",
            gis=self.gis
        )
        self.wm.basemap.basemap = new_basemap
        assert self.wm.extent["spatialReference"]["wkid"] != current_map_sr


if __name__ == "__main__":
    unittest.main()
