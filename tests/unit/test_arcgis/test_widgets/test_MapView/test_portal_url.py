import sys

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
sys.path.insert(1, r"C:\ipython_workfolder\geosaurus\tests")

import unittest
from arcgis.gis import GIS


class TestPortalUrl(unittest.TestCase):

    def test_portal_url_format(self):
        self._test_portal_url(
            profile="your_enterprise_profile",
            expected="https://pythonapi.playground.esri.com/portal",
        )

    def test_agol_standard(self):
        self._test_portal_url(
            profile=None,
            expected="https://www.arcgis.com",
        )

    def test_agol_subdomain(self):
        self._test_portal_url(
            profile="your_online_profile",
            expected="https://geosaurus.maps.arcgis.com",
        )

    def _test_portal_url(self, profile, expected):
        gis = GIS(profile=profile)
        mv = gis.map()
        assert expected == mv._get_portal_url()


if __name__ == "__main__":

    unittest.main()
