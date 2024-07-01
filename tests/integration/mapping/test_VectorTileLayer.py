from arcgis.gis import GIS
import unittest
import os
from arcgis.layers import VectorTileLayer
from utils.decorators import integration_test


@integration_test
class TestVectorTileLayerClass_online(unittest.TestCase):
    """
    Tests the Vector Tile Layer Class
    """

    @classmethod
    def setUpClass(cls):
        cls.vtl_id = "d720f1fc7b17466bac18b4533db25e03"
        cls.gis = GIS(profile="your_online_profile")

        cls.vtl_item = cls.gis.content.get(cls.vtl_id)
        cls.tl = VectorTileLayer.fromitem(cls.vtl_item)

    def test_properties(self):
        styles = self.tl.styles
        assert isinstance(styles, dict)

        info = self.tl.info
        assert info
        assert isinstance(info, list)

    def test_tile_fonts(self):
        fonts = self.tl.tile_fonts(fontstack="Arial Bold", stack_range="0-255")
        assert fonts

    def test_vector_tile(self):
        vt = self.tl.vector_tile(level="1", row="1", column="1")
        assert vt

    def test_tile_sprite(self):
        sprite = self.tl.tile_sprite()
        assert sprite
        assert isinstance(sprite, dict)

    def test_export_tiles(self):
        exported = self.tl.export_tiles(
            levels="0-2",
            export_extent={
                "xmin": -109.55,
                "ymin": 25.76,
                "xmax": -86.39,
                "ymax": 49.94,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            },
        )
        assert exported
        os.remove(exported[0])

    @classmethod
    def tearDownClass(cls):
        print("\n=============================================================")


class TestVectorTileLayerClass_enterprise(unittest.TestCase):
    """
    Tests the Vector Tile Layer Class
    """

    @classmethod
    def setUpClass(cls):
        cls.vtl_id = "b9fc667bd61540f6832e9a74139d640c"
        cls.gis = GIS(
            profile="your_enterprise_profile", verify_cert=False, trust_env=True
        )

        cls.vtl_item = cls.gis.content.get(cls.vtl_id)
        cls.tl = VectorTileLayer.fromitem(cls.vtl_item)

    def test_properties(self):
        styles = self.tl.styles
        assert isinstance(styles, dict)

        info = self.tl.info
        assert info
        assert isinstance(info, list)

    def test_tile_fonts(self):
        fonts = self.tl.tile_fonts(fontstack="Arial Bold", stack_range="0-255")
        assert fonts

    def test_vector_tile(self):
        vt = self.tl.vector_tile(level="1", row="1", column="1")
        assert vt

    def test_tile_sprite(self):
        sprite = self.tl.tile_sprite()
        assert sprite
        assert isinstance(sprite, dict)

    def test_export_tiles(self):
        exported = self.tl.export_tiles(
            levels="0-1",
        )
        assert exported

    @classmethod
    def tearDownClass(cls):
        print("\n=============================================================")


if __name__ == "__main__":
    unittest.main()
