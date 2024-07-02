import unittest
from arcgis.map import Map
from arcgis.features import FeatureLayer
from arcgis.layers import VectorTileLayer
from arcgis.gis import GIS

PROFILES = ["your_online_profile"]


class TestAddLayersToMap(unittest.TestCase):
    def test_vector_layer(self):
        """Test adding a vector tile layer as a basemap"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            # add layer
            layer = VectorTileLayer(
                "https://basemaps.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer"
            )
            assert layer

            wm.basemap.basemap = layer
            assert (
                wm.basemap.basemap["baseMapLayers"][0]["layerType"] == "VectorTileLayer"
            )
            wm.basemap.basemap_title(wm.basemap.basemap["baseMapLayers"][0]["title"])
            assert wm.basemap.basemap["title"] == layer.properties.name.replace(
                "_", " "
            )

    def test_basemaps_list(self):
        """Test adding each basemap in basemaps property as a basemap."""
        import time

        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            basemaps = wm.basemap.basemaps

            for basemap in basemaps:
                wm.basemap.basemap = basemap
                time.sleep(2)

    def test_invalid_basemap(self):
        """Test adding each basemap that isn't valid type."""

        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            layer = FeatureLayer(
                "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
            )
            try:
                wm.basemap.basemap = layer
                assert 1 == 2
            except Exception:
                # This should fail so it should end here
                assert 1 == 1

    def test_different_sr(self):
        """Test adding a basemap with a different spatial reference than original."""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm

            wm.basemap.basemap = gis.content.get("e67de4be72b349fd8f8ca114bac82a8c")
            assert wm


if __name__ == "__main__":
    unittest.main()
