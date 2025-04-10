import time
import unittest
from arcgis.map import Scene
from arcgis.layers import VectorTileLayer, MapServiceLayer, MapFeatureLayer
from utils.decorators import integration_test, profiles


@profiles.all
@integration_test
class TestAddLayersToScene(unittest.TestCase):

    def setUp(self):
        # create web scene
        self.ws = Scene(gis=self.gis)
        assert isinstance(self.ws, Scene)

    def test_vector_layer(self):
        """Test adding a vector tile layer as a basemap"""
        # add layer
        layer = VectorTileLayer(
            "https://basemaps.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer",
            gis=self.gis,
        )
        assert isinstance(layer, VectorTileLayer)

        self.ws.basemap.basemap = layer
        assert (
            self.ws.basemap.basemap["baseMapLayers"][0]["layerType"]
            == "VectorTileLayer"
        )
        self.ws.basemap.title = layer.properties.name
        
        assert self.ws.basemap.title == layer.properties.name.replace(
            "_", " "
        )

    def test_basemaps_list(self):
        """Test adding each basemap in basemaps property as a basemap."""
        basemaps = self.ws.basemap.basemaps

        for basemap in basemaps:
            self.ws.basemap.basemap = basemap
            assert basemap.replace("-", " ").lower() in self.ws.basemap.basemap["title"].lower()
            time.sleep(2)

    def test_invalid_basemap(self):
        """Test adding each basemap that isn't valid type."""
        try:
            self.ws.basemap.basemap = self.gis.content.get(
                "de5b947226ae4a67a94aa65cac9e20ff"
            )
            assert 1 == 2
        except:
            # This should fail so it should end here
            assert 1 == 1

    def test_different_sr(self):
        """Test adding a basemap with a different spatial reference than original."""
        current_scene_sr = self.ws.extent["spatialReference"]["wkid"]
        self.ws.basemap.basemap = self.gis.content.get(
            "e67de4be72b349fd8f8ca114bac82a8c"
        )
        # TODO: reminder for adding item to future k8s portal
        assert self.ws.extent["spatialReference"]["wkid"] != current_scene_sr


if __name__ == "__main__":
    unittest.main()
