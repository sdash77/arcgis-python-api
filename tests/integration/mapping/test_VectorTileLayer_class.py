import sys
import unittest

sys.path.insert(0, r"C:\\ipython_workfolder\\geosaurus_main\src")

from arcgis.mapping import VectorTileLayer
from arcgis.gis import GIS

gis = GIS(profile="your_online_profile")

# VectorTileLayer
item = gis.content.get("c98c939d961d463095199140dd30a75c")
layer = VectorTileLayer.fromitem(item)
print(layer)


class TestQueryFeatureLayer(unittest.TestCase):
    def test_tile_fonts(self):
        """"
        Test tile_fonts method
        """
        file = layer.tile_fonts(fontstack="Arial Bold", stack_range="0-255")
        assert isinstance(file, bytes)

    def test_vector_tile(self):
        """
        Test getting a single vector tile
        """
        tile = layer.vector_tile(level="0", row="0", column="0")
        assert isinstance(tile, bytes)

    def test_tile_sprites(self):
        """
        Test tile_sprites method
        """
        sprite = layer.tile_sprite()
        assert isinstance(sprite, dict)
        assert len(sprite) > 0

    def test_info(self):
        """"
        Test info property
        """
        info = layer.info
        assert isinstance(info, dict)
        assert "resourceInfo" in info


if __name__ == "__main__":
    unittest.main()
