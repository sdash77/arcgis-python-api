import unittest
import arcgis.auth

from utils.decorators import integration_test


@integration_test
class TestEsriSessionAnonymous(unittest.TestCase):
    """tests calling ArcGIS Online without any configuration"""

    def test_get(self):
        with arcgis.auth.EsriSession() as session:
            data = session.get(
                url="https://www.arcgis.com/sharing/rest/search",
                params={"f": "json", "q": "map"},
            ).json()
        assert "results" in data
        assert len(data["results"]) > 0

    def test_post(self):
        with arcgis.auth.EsriSession() as session:
            data = session.post(
                url="https://www.arcgis.com/sharing/rest/search",
                data={"f": "json", "q": "map"},
            ).json()
        assert "results" in data
        assert len(data["results"]) > 0


if __name__ == "__main__":
    unittest.main()
