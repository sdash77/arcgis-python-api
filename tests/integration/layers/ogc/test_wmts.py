import unittest
from arcgis.gis import GIS
from arcgis.layers._ogc import WMTSLayer
from utils.decorators import integration_test

wm_urls = {
    "earthdata": "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/1.0.0/WMTSCapabilities.xml",
    "world_tz": "https://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS",
    "quadrangles": "https://atlas2.wvgs.wvnet.edu/server/services/Hosted/Reference_Quadrangles/MapServer/WFSServer?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities",
    "santa_monica": "https://services3.arcgis.com/GVgbJbqm8hXASVYi/ArcGIS/rest/services/Santa_Monica_Mountains_Parcels_Styled_ITL/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
}


@integration_test
class TestWMTSLayer(unittest.TestCase):
    """Tests working with a wmts Layer"""

    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(profile="your_online_profile", verify_cert=False)

    def test_wfs_server(self):
        wm_url = wm_urls["earthdata"]
        wms = WMTSLayer(url=wm_url)
        self.assertIsInstance(wms, WMTSLayer, "Not a WMTS layer")

    def test_wmts_capabilities(self):
        wm_url = wm_urls["earthdata"]
        wmts = WMTSLayer(url=wm_url)
        self.assertIsInstance(wmts, WMTSLayer, f"Not a WMTS layer. Got: {type(wmts)}")
        self.assertEqual(
            1, wmts.opacity, f"Unexpected opacity value: Got: {wmts.opacity}"
        )

    def test_wmts(self):
        """tests the wmts Layer methods and properties"""
        wm_url = wm_urls["world_tz"]
        wmts = WMTSLayer(url=wm_url)
        assert isinstance(wmts, WMTSLayer), type(wmts)
        assert wmts.opacity == 1
        wmts.opacity = 0.5
        assert wmts.opacity == 0.5
        assert isinstance(wmts.scale, tuple)
        wmts.scale = (1, 2)
        assert wmts.scale == (1, 2)
        assert isinstance(wmts.title, str)
        wmts.title = "test"
        assert wmts.title == "test"
        assert wmts._lyr_json
        assert wmts.properties
        assert wmts.__text__

    def test_wfs_operational_lyr_json(self):
        wm_url = wm_urls["santa_monica"]
        wms = WMTSLayer(url=wm_url)
        layer_json = wms.operational_layer_json(
            "Santa_Monica_Mountains_Parcels_Styled_ITL"
        )
        self.assertIsNotNone(layer_json, "Operational layer JSON is None")

        tile_info = layer_json["tileInfo"]
        self.assertEqual(256, int(tile_info["rows"]))
        self.assertEqual(256, int(tile_info["cols"]))
        self.assertEqual(96, int(tile_info["dpi"]))


if __name__ == "__main__":
    unittest.main()
