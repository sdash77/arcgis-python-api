import os
import unittest
from arcgis.gis import GIS, ContentManager
from arcgis.features import FeatureLayer
from arcgis._impl.common._isd import InsensitiveDict
from utils.decorators import integration_test, profiles
from arcgis.auth.tools import LazyLoader
arcgismapping = LazyLoader("arcgis.map")


@profiles.agol
@integration_test
class TestRendererProperty(unittest.TestCase):
    def test_get_renderer(self):
        item = self.gis.content.search("*", "Feature Layer", outside_org=True)[0]
        lyr = item.layers[0]
        assert lyr.renderer
        assert isinstance(lyr.renderer, InsensitiveDict)

    def test_set_renderer(self):
        """test the setting the renderer manually based on the different data types"""
        item = self.gis.content.search("*", "Feature Layer", outside_org=True)[0]
        lyr = item.layers[0]
        r_property_map = lyr.properties.drawingInfo.renderer
        r_dict = dict(r_property_map)
        r_isd = InsensitiveDict(r_dict)
        r_none = None
        for r in [r_property_map, r_dict, r_isd, r_none]:
            lyr.renderer = r
            assert lyr.renderer
            assert isinstance(lyr.renderer, InsensitiveDict)

    def test_plot_mapview(self):
        item = self.gis.content.search("*", "Feature Layer", outside_org=True)[0]
        lyr = item.layers[0]
        wm = arcgismapping.Map()
        lyr.renderer.symbol.color = [0, 255, 0, 100]
        wm.content.add(lyr)
        assert list(wm.content.layers[0].renderer.symbol.color) == [0, 255, 0, 100]

    def test_plot_webmap(self):
        item = self.gis.content.search("*", "Feature Layer", outside_org=True)[0]
        lyr = item.layers[0]
        wm = arcgismapping.Map()
        lyr.renderer.symbol.color = [255, 0, 0, 100]
        wm.content.add(lyr)
        assert list(
            wm.content.layers[
                0
            ].layerDefinition.drawingInfo.renderer.symbol.color
        ) == [255, 0, 0, 100]


if __name__ == "__main__":
    unittest.main()
