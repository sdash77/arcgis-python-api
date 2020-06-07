import os
import unittest
import pytest

from arcgis.gis import GIS

from pathlib import Path


file_name = "RagS19004_gdb_pg.sde"
fp = str(Path(os.getcwd(), file_name))
if os.path.isfile(fp):
    SDEFOUND = True
else:
    SDEFOUND = False

@unittest.skipIf(SDEFOUND == False, "cannot find SDE file.")
class TestSDE2String(unittest.TestCase):
    """Tests the SDE to String helper GP tool"""
    def test_tool(self):
        """Tests the SDE to String helper GP tool"""
        
        gis = GIS(profile='your_enterprise_profile', verify_cert=False)
            
        servers = gis.admin.servers.list()
        server = servers[0]
        r = server.datastores.generate_connection_string(sde=fp)
        assert r.find("ENCRYPTED_PASSWORD=") > -1

if __name__ == "__main__":
    unittest.main()