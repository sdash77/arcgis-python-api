import sys

sys.path.insert(0, r"C:\\ipython_workfolder\\geosaurus\\src")
from arcgis.gis import GIS
import unittest
import os
from arcgis.mapping._types import VectorTileLayer

vector_tile_layers = []


class TestVectorTileLayerClass(unittest.TestCase):
    """
    Tests the Vetor Tile Layer Class
    """

    def test_fromitem_online(self):
        gis = GIS(profile="your_online_profile")
        vtl = VectorTileLayer.fromitem(
            gis.content.get("c98c939d961d463095199140dd30a75c")
        )
        assert vtl
        vector_tile_layers.append(vtl)

    def test_fromitem_ent(self):
        gis = GIS(profile="your_enterprise_profile")
        vtl = VectorTileLayer.fromitem(
            gis.content.get("5afcbf725cdb418798620b64ff330f18")
        )
        assert vtl
        vector_tile_layers.append(vtl)

    def test_properties(self):
        for tl in vector_tile_layers:
            styles = tl.styles
            assert isinstance(styles, dict)

            info = tl.info
            assert info
            assert isinstance(info, dict)

    def test_tile_fonts(self):
        for tl in vector_tile_layers:
            fonts = tl.tile_fonts(fontstack="Arial Bold", stack_range="0-255")
            assert fonts

    def test_vector_tile(self):
        for tl in vector_tile_layers:
            vt = tl.vector_tile(level="1", row="1", column="1")
            assert vt

    def test_tile_sprint(self):
        for tl in vector_tile_layers:
            sprite = tl.tile_sprite()
            assert sprite
            assert isinstance(sprite, dict)

    def test_export_tiles(self):
        for tl in vector_tile_layers:
            exported = tl.export_tiles(
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
            os.remove(exported)


if __name__ == "__main__":
    unittest.main()
