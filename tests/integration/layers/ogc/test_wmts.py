import unittest
from arcgis.gis import GIS
from arcgis.layers._ogc import WMTSLayer
from utils.decorators import integration_test

wm_urls = [
    # TODO replace infogis2 service with an esri-hosted or other public service
    "https://map.infogis2.ch/arcgis/rest/services/holderbank/holderbank_abwasser/MapServer/WMTS",
    "https://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS",
]


@integration_test
class TestwmtsLayer(unittest.TestCase):
    """Tests working with a wmts Layer"""

    def test_wmts(self):
        """tests the wmts Layer methods and properties"""
        gis = GIS(profile="your_online_profile", verify_cert=False)
        for wm_url in wm_urls:
            wmts = WMTSLayer(url=wm_url)
            assert isinstance(wmts, WMTSLayer)
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


if __name__ == "__main__":
    unittest.main()
