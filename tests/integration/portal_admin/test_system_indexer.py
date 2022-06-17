import sys
import unittest

sys.path.insert(0, r"C:\SVN\geosaurus_master_issue_7414\src")
from arcgis.gis import GIS

from arcgis.gis.admin._system import Indexer

url = "https://rqawinbi01pt.ags.esri.com/gis/home"
username = "PAPIadmin"
password = "PAPIletmein01"

gis = GIS(url, username, password, verify_cert=False, trust_env=True)


@unittest.skipIf(gis.version < [9, 2], reason="Portal is too old!")
class TestPortalIndexer(unittest.TestCase):
    def test_get_indexer(self):
        """tests that the right class is returned."""
        assert isinstance(gis.admin.system.indexer, Indexer)

    def test_status(self):
        """tests the status functionality of the Indexer"""
        indexer = gis.admin.system.indexer
        status = indexer.status
        assert status
        assert "indexes" in status or "status" in status

    def test_reindex(self):
        indexer = gis.admin.system.indexer
        assert indexer.reindex("USER_MODE")

    @unittest.skip(reason="manual test only")
    def test_reconfigure(self):
        indexer = gis.admin.system.indexer
        assert indexer.reconfigure()


if __name__ == "__main__":
    unittest.main()
