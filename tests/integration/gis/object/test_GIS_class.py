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
        self.assertGreaterEqual(
            len(gis_properties), 20, "gis.properties may not be fully hydrated"
        )
        if self.gis._is_agol:
            self.assertFalse(gis_properties["isPortal"])
        else:
            self.assertTrue(gis_properties["isPortal"])

        assert "portalProperties" in gis_properties
        assert "user" in gis_properties

if __name__ == "__main__":
    unittest.main()


