import unittest
import os
import sys
from arcgis.gis import *

# add needed root paths to sys.path
cwd = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(cwd))
sys.path.append(root_dir)
import shared_utils.shared_utils as utils



class TestToolsGeocoder_Reversegeocode(unittest.TestCase):
    __owner__ = "Kevin"
    
    @classmethod
    def setUpClass(self):
        srvProps = utils.get_server_info(os.path.join(root_dir, 'unittest.ini'))
        self.host = srvProps['url']
        self.username = srvProps['admin_user']
        self.password = srvProps['admin_pass']
        self.arcgiscom = True if "arcgis.com" in self.host else False
        self.local = False if self.arcgiscom else True
        self.gis = GIS(self.host, self.username, self.password)
        
    def tearDown(self):
        '''anything needed for clean up in here'''
        pass
    
    def testGeocoderURL(self):
        geocode = self.gis.tools.geocoder
        url = geocode.url
        if self.arcgiscom:
            self.assertEqual(url, 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer')
        elif self.local:
            self.assertEqual(url, "LocalPortalVar")  #maybe get from ini         
  
    def testReverseGeocoder(self):
        
        revgeo = self.gis.tools.geocoder
        revres = revgeo.reverse_geocode([-117.195936, 34.056761])
        self.assertIsNotNone(revres, "None response on address")
        self.assertEqual(revres['address']['CountryCode'], "USA")
        self.assertEqual(revres['address']['Address'], "370 N New York St")
    
    def invalidReverseGeocoder(self):
        
        revgeo = self.gis.tools.geocoder
        gcrest = revgeo.reverse_geocode(("123", "456"))
        self.assertRaises("Invalid location")


if __name__ == '__main__':
    unittest.main()