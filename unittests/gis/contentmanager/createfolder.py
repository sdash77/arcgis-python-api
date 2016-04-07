import unittest
import os
import sys
from arcgis.gis import *

# add needed root paths to sys.path
cwd = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(cwd))
sys.path.append(root_dir)
import shared_utils.shared_utils as utils


class TestGISContentManager_Createfolder(unittest.TestCase):
    __owner__ = "Kevin"
    
    @classmethod
    def setUpClass(self):
        srvProps = utils.get_server_info(os.path.join(root_dir, 'unittest.ini'))
        self.username = username
        self.password = password
        self.host = url
        self.arcgiscom = True
        self.local = False
        self.gis = GIS(self.host, self.username, self.password)
        
    def tearDown(self):
        '''anything needed for clean up in here'''
        pass
    
    def _testSomething(self):
        pass


if __name__ == '__main__':
    unittest.main()