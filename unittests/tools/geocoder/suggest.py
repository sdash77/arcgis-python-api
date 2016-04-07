import unittest
import os
import sys
from arcgis.gis import *

# add needed root paths to sys.path
cwd = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(cwd))
sys.path.append(root_dir)
import shared_utils.shared_utils as utils


class TestToolsGeocoder_Suggest(unittest.TestCase):
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
            self.assertEqual(url, self.host + "/services/World/GeocodeServer")
    
    @unittest.skip("not working with arcgis.com")
    def testGeocodeSuggest(self):
        geocode = self.gis.tools.geocoder
        if self.arcgiscom:
            #seems arcgis.com throws invalid token
            # think its specific to suggestions
            pass            
        else:
            sugres = geocode.suggest("Esri", [-117.19, 34.05])
            self.assertEqual(sugres, "Esri location")
    

if __name__ == '__main__':
    unittest.main()