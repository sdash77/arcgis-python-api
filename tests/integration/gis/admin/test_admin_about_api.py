import sys
import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging
from functools import lru_cache
enable_verbose_logging()
from arcgis.gis import GIS
from arcgis.gis.admin._about import AboutManager

@lru_cache(maxsize=128)
def _version_checker():
    gis = GIS(profile='your_ent_admin_profile')
    version = tuple(gis.version)
    return version
    
@integration_test
class TestAboutEnterprise(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(profile='your_ent_admin_profile', verify_cert=False, trust_env=True)
    
    @unittest.skipIf(list(_version_checker()) < [2025, 1], "enterprise does not support `about`")
    def test_about(self):
        assert isinstance(self.gis.admin.about, AboutManager)
    
    @unittest.skipIf(list(_version_checker()) < [2025, 1], "enterprise does not support `about`")
    def test_about_export(self):
        about = self.gis.admin.about
        assert about.properties
        assert about.report(redact=False)
        assert about.report(redact=True)
        assert isinstance(self.gis.admin.about, AboutManager)    


if __name__ == "__main__":
    unittest.main()