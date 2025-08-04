import uuid
import time
import unittest
from arcgis._impl.common._isd import InsensitiveDict
from arcgis.gis import ItemTypeEnum
from integration.config import get_resource_path
from utils.decorators import integration_test, profiles
from utils.data_utils import publish_test_item, cleanup_published_items
from arcgis.auth.tools import LazyLoader

arcgismapping = LazyLoader("arcgis.map")


@profiles.agol
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
        wm = arcgismapping.Map()
        self.assertIsNotNone(wm, "Map is None")
        rrr = lyr.renderer
        rrr.symbol.color = [0, 255, 0, 100]
        wm.content.add(lyr, {"title": f"fl_renderer_{self.uid}", "tags": "ntgrtn-tst"})
        assert list(wm.content.layers[0].renderer.symbol.color) == [0, 255, 0, 100]

    def test_plot_webmap(self):
        lyr = self.item.layers[0]
        wm = arcgismapping.Map()
        self.assertIsNotNone(wm, "Map is None")
        lyr.renderer.symbol.color = [255, 0, 0, 100]
        wm.content.add(lyr, {"title": f"fl_renderer_{self.uid}", "tags": "ntgrtn-tst"})
        wm_fl = wm.content.layers[0]
        assert list(wm_fl.renderer.symbol.color) == [
            255,
            0,
            0,
            100,
        ]

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items([cls.item])


if __name__ == "__main__":
    unittest.main()
