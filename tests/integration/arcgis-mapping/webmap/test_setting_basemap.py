import time
import unittest
from arcgis.map import Map
from arcgis.features import FeatureLayer
from arcgis.layers import VectorTileLayer
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestAddLayersToMap(unittest.TestCase):

    def setUp(self):
        # create webmap
        self.wm = Map(gis=self.gis)
        assert self.wm

    def test_vector_layer(self):
        """Test adding a vector tile layer as a basemap"""

        # add layer
        layer = VectorTileLayer(
            "https://basemaps.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer",
            gis=self.gis,
        )
        assert layer

        self.wm.basemap.basemap = layer
        assert (
                self.wm.basemap.basemap["baseMapLayers"][0]["layerType"] == "VectorTileLayer"
        )
        self.wm.basemap.basemap_title(self.wm.basemap.basemap["baseMapLayers"][0]["title"])
        assert self.wm.basemap.basemap["title"] == layer.properties.name.replace(
            "_", " "
        )

    def test_basemaps_list(self):
        """Test adding each basemap in basemaps property as a basemap."""

        basemaps = self.wm.basemap.basemaps

        for basemap in basemaps:
            self.wm.basemap.basemap = basemap
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
        self.wm.basemap.basemap = self.gis.content.get("e67de4be72b349fd8f8ca114bac82a8c")
        assert self.wm


if __name__ == "__main__":
    unittest.main()
