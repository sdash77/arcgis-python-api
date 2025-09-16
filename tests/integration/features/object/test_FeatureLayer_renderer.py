import uuid

import unittest
from arcgis._impl.common._isd import InsensitiveDict
from arcgis.gis import GIS, ItemTypeEnum
from integration.config import get_resource_path
from utils.decorators import integration_test, profiles
from utils.data_utils import publish_test_item, cleanup_published_items

from arcgis.map import Map


@profiles.enterprise
@integration_test
class TestRendererProperty(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.uid = uuid.uuid4().hex[:4]
        restaurants = get_resource_path(
            "staging_data/parkinglots.zip", unique_copy=True
        )
        cls.item = publish_test_item(
            cls.gis,
            f"fl_renderer_{cls.uid}",
            restaurants,
            ItemTypeEnum.SHAPEFILE,
            prep_for_editing=True,
        )
        cls.layers = cls.item.layers

        cls.new_renderer = {
            "type": "simple",
            "symbol": {
                "type": "esriSFS",
                "style": "esriSFSSolid",
                "color": [0, 255, 0, 100],
                "outline": {
                    "type": "esriSLS",
                    "style": "esriSLSSolid",
                    "color": [0, 0, 0, 255],
                    "width": 0.75,
                },
            },
        }

    def test_get_renderer(self):
        lyr = self.item.layers[0]
        assert lyr.renderer
        assert isinstance(lyr.renderer, InsensitiveDict)

    def test_set_renderer(self):
        """test the setting the renderer manually based on the different data types"""
        lyr = self.item.layers[0]
        r_property_map = lyr.properties.drawingInfo.renderer
        r_dict = dict(r_property_map)
        r_isd = InsensitiveDict(r_dict)
        r_none = None
        for r in [r_property_map, r_dict, r_isd, r_none]:
            lyr.renderer = r
            assert lyr.renderer
            assert isinstance(lyr.renderer, InsensitiveDict)

    def test_plot_mapview(self):
        lyr = self.item.layers[0]
        wm = Map()
        self.assertIsNotNone(wm, "Map is None")
        wm.content.add(
            lyr,
            {
                "title": f"fl_renderer_{self.uid}",
                "tags": "ntgrtn-tst",
            },
        )
        wm.content.layers[0].renderer = self.new_renderer
        wm_symbol_color = wm.content.layers[0].renderer.symbol.color
        assert list(wm_symbol_color) == [0, 255, 0, 100], f"Got {wm_symbol_color}"

    def test_plot_webmap(self):
        lyr = self.item.layers[0]
        wm = Map()
        self.assertIsNotNone(wm, "Map is None")
        lyr.renderer.symbol.color = [255, 0, 0, 100]
        wm.content.add(lyr, {"title": f"fl_renderer_{self.uid}", "tags": "ntgrtn-tst"})
        wm_fl = wm.content.layers[0]
        wm_fl.renderer = self.new_renderer
        wm_fl_symbol_color = wm_fl.renderer.symbol.color
        assert list(wm_fl_symbol_color) == [
            0,
            255,
            0,
            100,
        ], f"Got: {wm_fl_symbol_color}"

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items([cls.item])


if __name__ == "__main__":
    unittest.main()
