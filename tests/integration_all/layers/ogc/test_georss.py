import unittest
from arcgis.layers import GeoRSSLayer
from utils.decorators import integration_test

geo_rss_url = "https://arcgis.github.io/arcgis-samples-javascript/sample-data/layers-georss/sample-georss.xml"


@integration_test
class TestGeoRSSLayer(unittest.TestCase):
    """Tests working with a GeoRss Layer"""

    def test_georss(self):
        """tests the georss methods and properties"""
        georss = GeoRSSLayer(url=geo_rss_url)
        assert isinstance(georss, GeoRSSLayer)
        assert georss.line_symbol
        assert georss.opacity == 1
        georss.opacity = 0.5
        assert georss.opacity == 0.5
        assert georss.point_symbol
        assert georss.polygon_symbol
        assert isinstance(georss.scale, tuple)
        georss.scale = (1, 2)
        assert georss.scale == (1, 2)
        assert isinstance(georss.title, str)
        georss.title = "test"
        assert georss.title == "test"
        assert georss._lyr_json
        assert georss.properties
        print(georss.properties)


if __name__ == "__main__":
    unittest.main()
