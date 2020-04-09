"""
This is 10.8.1+ Functionality Tests for Notebook Server
"""
import unittest
import os, json
import arcgis
from arcgis.gis import GIS
from arcgis.gis.nb import NotebookServer, NotebookManager

try:
    url = "https://datasciencedev.esri.com/portal"
    username = "portaladmin"
    password = 'esri.agp'
    gis = GIS(url=url, username=username, password=password, verify_cert=False)
    SKIP_TESTS = False
except:
    SKIP_TESTS = True

@unittest.skipIf(SKIP_TESTS == True, 
                 "Cannot connect to Testing Server and/or Portal")
class TestNotebookServer1081(unittest.TestCase):
    """Tests New 10.8.1 Functionality"""
    
    def test_recent_stats(self):
        """tests the recent statistics"""
        servers = gis.admin.servers.list()
        for server in gis.admin.servers.list():
            if isinstance(server, NotebookServer):
                break
        assert server.system.recent_statistics
        assert isinstance(server.system.recent_statistics, dict)
        
if __name__ == "__main__":
    unittest.main()