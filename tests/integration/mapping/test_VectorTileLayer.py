import sys
sys.path.insert(0, r"C:\Job\repos\geosaurus\src")

from arcgis.gis import GIS
import unittest
import os
from arcgis.mapping._types import VectorTileLayer

vector_tile_layers = []

class TestVectorTileLayerClass_online(unittest.TestCase):
    """
    Tests the Vector Tile Layer Class
    """
    
    @classmethod
    def setUpClass(cls):
        cls.vtl_id = "c98c939d961d463095199140dd30a75c"
        cls.gis = GIS(profile="your_online_admin_profile")
        
        cls.vtl_item = cls.gis.content.get(cls.vtl_id)
        vector_tile_layers.append(cls.vtl_item)
        
    def test_properties(self):
        for vtitem in vector_tile_layers:
            tl = VectorTileLayer.fromitem(vtitem)
            styles = tl.styles
            assert isinstance(styles, dict)

            info = tl.info
            assert info
            assert isinstance(info, dict)

    def test_tile_fonts(self):              
        for vtitem in vector_tile_layers:
            tl = VectorTileLayer.fromitem(vtitem)
            fonts = tl.tile_fonts(fontstack="Arial Bold", stack_range="0-255")
            assert fonts

    def test_vector_tile(self):
        for vtitem in vector_tile_layers:
            tl = VectorTileLayer.fromitem(vtitem)
            vt = tl.vector_tile(level="1", row="1", column="1")
            assert vt

    def test_tile_sprint(self):
        for vtitem in vector_tile_layers:
            tl = VectorTileLayer(vtitem)
            sprite = tl.tile_sprite()
            assert sprite
            assert isinstance(sprite, dict)

    def test_export_tiles(self):
        for vtitem in vector_tile_layers:
            tl = VectorTileLayer.fromitem(vtitem)
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
            os.remove(exported[0])
    
    @classmethod
    def tearDownClass(cls):
        vector_tile_layers.pop(0)
        print("\n=============================================================")
        
class TestVectorTileLayerClass_enterprise(unittest.TestCase):
    """
    Tests the Vector Tile Layer Class
    """
    
    @classmethod
    def setUpClass(cls):
        cls.vtl_id = "5afcbf725cdb418798620b64ff330f18"
        cls.gis = GIS(profile="your_ent_admin_profile", verify_cert=False, trust_env=True)

        cls.vtl_item = cls.gis.content.get(cls.vtl_id)
        vector_tile_layers.append(cls.vtl_item)
        
    def test_properties(self):
        for vtitem in vector_tile_layers:
            tl = VectorTileLayer.fromitem(vtitem)
            styles = tl.styles
            assert isinstance(styles, dict)

            info = tl.info
            assert info
            assert isinstance(info, dict)

    def test_tile_fonts(self):       
        for vtitem in vector_tile_layers:
            tl = VectorTileLayer.fromitem(vtitem)
            fonts = tl.tile_fonts(fontstack="Arial Bold", stack_range="0-255")
            assert fonts

    def test_vector_tile(self):       
        for vtitem in vector_tile_layers:
            tl = VectorTileLayer.fromitem(vtitem)
            vt = tl.vector_tile(level="1", row="1", column="1")
            assert vt

    def test_tile_sprint(self):
        for vtitem in vector_tile_layers:
            tl = VectorTileLayer(vtitem)
            sprite = tl.tile_sprite()
            assert sprite
            assert isinstance(sprite, dict)

    def test_export_tiles(self):           
        for vtitem in vector_tile_layers:
            tl = VectorTileLayer.fromitem(vtitem)
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
            os.remove(exported[0])

    @classmethod
    def tearDownClass(cls):
        vector_tile_layers.pop(0)
        print("\n=============================================================")

if __name__ == "__main__":
    unittest.main()
