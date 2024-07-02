import unittest
from arcgis.map import Map, GroupLayer
from arcgis.features import FeatureLayer
from arcgis.layers import (
    VectorTileLayer,
    CSVLayer,
)
from arcgis.gis import GIS

PROFILES = ["your_online_profile"]


class TestAddLayersToMap(unittest.TestCase):
    def test_add_as_group(self):
        """Test adding a feature layer"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            # add layer
            layer = FeatureLayer(
                "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
            )
            layer2 = VectorTileLayer(
                "https://basemaps.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer"
            )
            layer3 = CSVLayer(
                "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.csv"
            )

            assert layer
            wm.content.add([layer, layer2, layer3])
            assert wm.content.layers
            assert len(wm.content.layers) == 1
            assert isinstance(wm.content.layers[0], GroupLayer)

    def test_ungroup(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            # add layer
            layer = FeatureLayer(
                "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
            )
            layer2 = VectorTileLayer(
                "https://basemaps.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer"
            )
            layer3 = CSVLayer(
                "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.csv"
            )

            assert layer
            wm.content.add([layer, layer2, layer3])
            assert wm.content.layers
            assert len(wm.content.layers) == 1
            assert isinstance(wm.content.layers[0], GroupLayer)

            wm.content.layers[0].ungroup()
            assert len(wm.content.layers) == 3
            assert isinstance(wm.content.layers[0], FeatureLayer)
            assert isinstance(wm.content.layers[1], VectorTileLayer)
            assert isinstance(wm.content.layers[2], CSVLayer)

    def test_move(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            # add layer
            layer = FeatureLayer(
                "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
            )
            layer2 = VectorTileLayer(
                "https://basemaps.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer"
            )
            layer3 = CSVLayer(
                "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.csv"
            )

            assert layer
            wm.content.add([layer, layer2, layer3])
            assert wm.content.layers
            assert len(wm.content.layers) == 1
            assert isinstance(wm.content.layers[0], GroupLayer)

            wm.content.layers[0].move(1)
            assert len(wm.content.layers) == 2


if __name__ == "__main__":
    unittest.main()
