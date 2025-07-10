import sys
import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging
from functools import lru_cache
enable_verbose_logging()
from arcgis.gis import GIS

@lru_cache(maxsize=128)
def _version_checker():
    gis = GIS(profile='your_ent_admin_profile')
    version = tuple(gis.version)
    return version
    
@integration_test
class TestMisMatchEnterprise(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(profile='your_ent_admin_profile', verify_cert=False, trust_env=True)
    
    @unittest.skipIf(list(_version_checker()) < [2025, 1], "enterprise does not support `about`")
    def test_about(self):
        val = self.gis.admin.system.indexer.mismatch
        assert isinstance(val, dict)
        assert "status" in val


if __name__ == "__main__":
    unittest.main()