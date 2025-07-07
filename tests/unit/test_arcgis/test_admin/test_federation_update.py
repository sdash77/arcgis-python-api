import unittest
from arcgis.gis.admin import Federation
from arcgis.gis import GIS

class TestFederationParams(unittest.TestCase):
    def setUp(self):
        # You can use a mock or dummy for the GIS and URL
        self.fed = Federation("https://dummy/portal/admin", gis=GIS())

    def test_valid_role_and_function(self):
        params = self.fed._build_update_params("hosting_server", ["GeoAnalytics", "NotebookServer"])
        self.assertEqual(params["serverRole"], "HOSTING_SERVER")
        self.assertIn("GeoAnalytics", params["serverFunction"])
        self.assertIn("NotebookServer", params["serverFunction"])

    def test_invalid_role(self):
        with self.assertRaises(ValueError):
            self.fed._build_update_params("INVALID_ROLE", None)

    def test_invalid_function(self):
        with self.assertRaises(ValueError):
            self.fed._build_update_params("HOSTING_SERVER", ["GeoAnalytics", "BadFunction"])

    def test_function_as_string(self):
        params = self.fed._build_update_params("FEDERATED_SERVER", "ImageHosting")
        self.assertEqual(params["serverFunction"], "ImageHosting")

    def test_no_function(self):
        params = self.fed._build_update_params("FEDERATED_SERVER", None)
        self.assertNotIn("serverFunction", params)

if __name__ == "__main__":
    unittest.main()