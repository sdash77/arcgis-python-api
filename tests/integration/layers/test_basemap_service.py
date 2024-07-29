from arcgis.layers._basemap.basemap_service import BasemapServices
from arcgis.gis import GIS
import unittest
from utils.decorators import integration_test

profiles = ['your_online_profile', 'test_enterprise']

@integration_test
class Test_BasemapService(unittest.TestCase):
    """Tests Basemap Service Class"""
    def test_get_styles(self):
        """Tests getting styles"""
        for profile in profiles:
            gis = GIS(profile=profile)
            bs = BasemapServices(gis)
            styles = bs.styles
            self.assertTrue(isinstance(styles, list))
            self.assertTrue(len(styles) > 0)
    
    def test_get_languages(self):
        """Tests getting languages"""
        for profile in profiles:
            gis = GIS(profile=profile)
            bs = BasemapServices(gis)
            languages = bs.languages
            self.assertTrue(isinstance(languages, list))
            self.assertTrue(len(languages) > 0)

    def test_get_places(self):
        """Tests getting places"""
        for profile in profiles:
            gis = GIS(profile=profile)
            bs = BasemapServices(gis)
            places = bs.places
            self.assertTrue(isinstance(places, list))
            self.assertTrue(len(places) > 0)

if __name__ == "__main__":
    unittest.main()