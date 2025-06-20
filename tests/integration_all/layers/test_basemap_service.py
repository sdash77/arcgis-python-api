from arcgis.layers._basemap.basemap_service import BasemapServices, BasemapService
from arcgis.gis import GIS
import unittest
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class Test_BasemapService(unittest.TestCase):
    """Tests Basemap Service Class"""

    def test_get_services(self):
        """Tests getting styles"""
        gis = self.gis
        bs = BasemapServices(gis)
        services = bs.services
        self.assertTrue(isinstance(services, list))
        self.assertTrue(len(services) > 0)
        self.assertTrue(isinstance(services[0], BasemapService))

        style = services[0].style
        self.assertTrue(isinstance(style, dict))

    def test_get_languages(self):
        """Tests getting languages"""
        gis = self.gis
        bs = BasemapServices(gis)
        languages = bs.languages
        self.assertTrue(isinstance(languages, list))
        self.assertTrue(len(languages) > 0)

    def test_get_places(self):
        """Tests getting places"""
        gis = self.gis
        bs = BasemapServices(gis)
        places = bs.places
        self.assertTrue(isinstance(places, list))
        self.assertTrue(len(places) > 0)


if __name__ == "__main__":
    unittest.main()
