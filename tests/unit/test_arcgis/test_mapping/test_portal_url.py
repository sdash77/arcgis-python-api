import unittest
from arcgis.gis import GIS


class TestPortalUrl(unittest.TestCase):

    def test_portal_url_format(self):
        self._test_portal_url(
            url = "https://pythonapi.playground.esri.com/portal",
            username = "arcgis_python",
            password = "amazing_arcgis_123",
            expected="https://pythonapi.playground.esri.com/portal",
        )

    def test_agol_standard(self):
        self._test_portal_url(
            url=None,
            username= None,
            password=None,
            expected="https://www.arcgis.com",
        )

    def test_agol_subdomain(self):
        self._test_portal_url(
            url= "https://geosaurus.maps.arcgis.com",
            username= "ArcGISPyAPIBot",
            password= "geosaurus_automation123",
            expected="https://geosaurus.maps.arcgis.com",
        )

    def _test_portal_url(self, url, username, password, expected):
        gis = GIS(url=url, username=username, password=password)
        mv = gis.map()
        assert expected == mv._get_portal_url()


if __name__ == "__main__":

    unittest.main()
