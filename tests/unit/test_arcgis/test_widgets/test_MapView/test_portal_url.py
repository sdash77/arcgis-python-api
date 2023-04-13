import unittest
from unittest.mock import patch, MagicMock

from utils.mocks import MockMapView
from arcgis.widgets import MapView


class TestPortalUrl(unittest.TestCase):

    def test_portal_url_format(self):
        self._test_portal_url(
            mock_rest_url="https://pythonapi.playground.esri.com/portal/sharing/rest/",
            expected="https://pythonapi.playground.esri.com/portal",
        )

    def test_agol_standard(self):
        self._test_portal_url(
            mock_rest_url="https://www.arcgis.com/sharing/rest/",
            expected="https://www.arcgis.com",
        )

    def test_agol_subdomain(self):
        self._test_portal_url(
            mock_rest_url="https://geosaurus.maps.arcgis.com/sharing/rest/",
            expected="https://geosaurus.maps.arcgis.com",
        )

    def _test_portal_url(self, mock_rest_url, expected):
        mock_mapview = MockMapView()
        mock_mapview.gis._portal.resturl = mock_rest_url
        assert expected == MapView._get_portal_url(mock_mapview)


if __name__ == "__main__":

    unittest.main()
