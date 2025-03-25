import unittest
from utils.decorators import integration_test, profiles


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


@profiles.all
@integration_test
class TestCheckUrl(unittest.TestCase):
    """Tests the check url functionality on the ContentManager class"""

    def test_invalid_url(self):
        """tests a invalid url that should return false in the dictionary response"""
        for url in URLS["BAD"]:
            r = self.gis.content.check_url(url)
            assert "success" in r or "httpStatusMessage" in r

    def test_valid_url(self):
        """tests a valid url that should return true in the dictionary response"""
        for url in URLS["GOOD"]:
            r = self.gis.content.check_url(url)
            assert "success" in r or "httpStatusMessage" in r


if __name__ == "__main__":
    unittest.main()
