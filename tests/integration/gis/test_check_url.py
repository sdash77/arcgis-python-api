import unittest

from arcgis.gis import GIS
from utils.decorators import integration_test

PROFILES = ["your_online_profile", "your_enterprise_profile"]


URLS = {
    "GOOD": [
        "https://www.arcgis.com/sharing/rest/portals/self",
        "https://google.com",
        "https://www.amazon.com",
    ],
    "BAD": [
        "http://idonotexist",
        "www.arcgis.com",
        "https://github.com/arcgis/fakerepo",
    ],
}


@integration_test
class TestCheckUrl(unittest.TestCase):
    """Tests the check url functionality on the ContentManager class"""

    def test_invalid_url(self):
        """tests an invalid url that should return false in the dictionary response"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)
            for url in URLS["BAD"]:
                r = gis.content.check_url(url)
                assert "success" in r or "httpStatusMessage" in r

    def test_valid_url(self):
        """tests an valid url that should return true in the dictionary response"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)
            for url in URLS["GOOD"]:
                r = gis.content.check_url(url)
                assert "success" in r or "httpStatusMessage" in r


if __name__ == "__main__":
    unittest.main()
