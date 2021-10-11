import sys

# sys.path.insert(0, r"c:\SVN\geosaurus_master_issue_4790a\src")
import unittest
import arcgis.auth


class TestAnonymousTests(unittest.TestCase):
    """tests calling ArcGIS Online without any handlers"""

    def test_get(self):
        session = arcgis.auth.EsriSession()
        data = session.get(
            url="https://www.arcgis.com/sharing/rest/search",
            params={"f": "json", "q": "map"},
        ).json()
        assert "results" in data
        session.close()

    def test_post(self):
        session = arcgis.auth.EsriSession()
        data = session.post(
            url="https://www.arcgis.com/sharing/rest/search",
            data={"f": "json", "q": "map"},
        ).json()
        assert "results" in data
        session.close()


if __name__ == "__main__":
    unittest.main()
