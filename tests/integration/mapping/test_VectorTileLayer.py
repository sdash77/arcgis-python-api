import sys

# sys.path.insert(0, r"<path_to_repo>\geosaurus\src")

from arcgis.gis import GIS
import unittest
import os
from arcgis.mapping._types import VectorTileLayer


class TestVectorTileLayerClass_online(unittest.TestCase):
    """
    Tests the Vector Tile Layer Class
    """

    @classmethod
    def setUpClass(cls):
        cls.vtl_id = "c98c939d961d463095199140dd30a75c"
        cls.gis = GIS(profile="your_online_admin_profile")

        cls.vtl_item = cls.gis.content.get(cls.vtl_id)
        cls.tl = VectorTileLayer.fromitem(cls.vtl_item)

    def test_properties(self):
        styles = self.tl.styles
        assert isinstance(styles, dict)

        info = self.tl.info
        assert info
        assert isinstance(info, dict)

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
            max_export_tile_count=500,
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
        cls.vtl_id = "5afcbf725cdb418798620b64ff330f18"
        cls.gis = GIS(
            profile="your_ent_admin_profile", verify_cert=False, trust_env=True
        )

        cls.vtl_item = cls.gis.content.get(cls.vtl_id)
        cls.tl = VectorTileLayer.fromitem(cls.vtl_item)

    def test_properties(self):
        styles = self.tl.styles
        assert isinstance(styles, dict)

        info = self.tl.info
        assert info
        assert isinstance(info, dict)

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
            max_export_tile_count=500,
        )
        assert exported
        os.remove(exported[0])

    @classmethod
    def tearDownClass(cls):
        print("\n=============================================================")


if __name__ == "__main__":
    unittest.main()
