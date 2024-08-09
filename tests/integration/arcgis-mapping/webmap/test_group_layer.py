import unittest
from arcgis.map import Map, GroupLayer
from arcgis.features import FeatureLayer
from arcgis.layers import (
    VectorTileLayer,
    CSVLayer,
)
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestAddLayersToMap(unittest.TestCase):

    def setUp(self):

        # create webmap
        self.wm = Map(gis=self.gis)
        assert self.wm

        # create layer
        self.layer = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        self.layer2 = VectorTileLayer(
            "https://basemaps.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer",
            gis=self.gis,
        )
        self.layer3 = CSVLayer(
            "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.csv"
        )
        assert self.layer
        assert self.layer2
        assert self.layer3

    def test_add_as_group(self):
        """Test adding a feature layer"""

        self.wm.content.add([self.layer, self.layer2, self.layer3])
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], GroupLayer)

    def test_ungroup(self):

        self.wm.content.add([self.layer, self.layer2, self.layer3])
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], GroupLayer)

        self.wm.content.layers[0].ungroup()
        assert len(self.wm.content.layers) == 3
        assert isinstance(self.wm.content.layers[0], FeatureLayer)
        assert isinstance(self.wm.content.layers[1], VectorTileLayer)
        assert isinstance(self.wm.content.layers[2], CSVLayer)

    def test_move(self):

        self.wm.content.add([self.layer, self.layer2, self.layer3])
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], GroupLayer)

        self.wm.content.layers[0].move(1)
        assert len(self.wm.content.layers) == 2


if __name__ == "__main__":
    unittest.main()
