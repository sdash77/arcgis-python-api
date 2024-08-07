import unittest
from utils.decorators import integration_test, profiles

@integration_test
@profiles.enterprise_and_agol
class TestGISClass(unittest.TestCase):
    """
    Test to check if a GIS object can be created with AGOL and enterprise
    """

    def test_sign_in(self):
        self.assertIsNotNone(self.gis, "Cannot sign into portal")

    def test_properties(self):
        gis_properties = self.gis.properties
        self.assertIsNotNone(gis_properties, "gis.properties returns None")
        # weak assertion
        self.assertGreaterEqual(
            len(gis_properties), 20, "gis.properties may not be fully hydrated"
        )

if __name__ == "__main__":
    unittest.main()
