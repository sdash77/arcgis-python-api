import unittest
from arcgis.gis.admin import Federation

class TestFederationParams(unittest.TestCase):

    def test_valid_role_and_function(self):
        params = Federation._build_update_params("hosting_server", ["GeoAnalytics", "NotebookServer"])
        self.assertEqual(params["serverRole"], "HOSTING_SERVER")
        self.assertIn("GeoAnalytics", params["serverFunction"])
        self.assertIn("NotebookServer", params["serverFunction"])

    def test_invalid_role(self):
        with self.assertRaises(ValueError):
            Federation._build_update_params("INVALID_ROLE", None)

    def test_invalid_function(self):
        with self.assertRaises(ValueError):
            Federation._build_update_params("HOSTING_SERVER", ["GeoAnalytics", "BadFunction"])

    def test_function_as_string(self):
        params = Federation._build_update_params("FEDERATED_SERVER", "ImageHosting")
        self.assertEqual(params["serverFunction"], "ImageHosting")

    def test_no_function(self):
        params = Federation._build_update_params("FEDERATED_SERVER", None)
        self.assertNotIn("serverFunction", params)

if __name__ == "__main__":
    unittest.main()