import unittest
from utils._logging import enable_verbose_logging
from utils.decorators import integration_test, profiles

import arcgis

enable_verbose_logging()


@unittest.skip("Manual test, comment this decorator to run")
@profiles.admin_enterprise
@integration_test
class TestMode(unittest.TestCase):
    def test_set_readonly(self):
        """tests setting the portal to read only mode"""
        assert self.gis
        assert self.gis.users.me
        self.gis.admin.mode = {'read_only': True}
        assert self.gis.admin.mode
        assert self.gis.admin.mode.get('isReadOnly') is True, "Expected read only mode to be True"

        self.gis.admin.mode = None
        assert self.gis.admin.mode.get('isReadOnly') is False, "Expected read only mode to be False"
    
    def test_set_readonly_reconnect(self):
        """tests setting the portal to read only mode, checking reconnect"""
        assert self.gis, "Expected GIS object to be available"
        assert self.gis.users.me, "Expected authenticated user to be available"
        self.gis.admin.mode = {'read_only': True}
        assert self.gis.admin.mode
        assert self.gis.admin.mode.get('isReadOnly') is True, "Expected read only mode to be True"

        reconnected_gis = arcgis.gis.GIS(profile=self.profile, proxy=self.proxies, verify_cert=False)
        assert reconnected_gis.users.me
        assert reconnected_gis.admin, "Expected admin property to be available after reconnect"
        assert reconnected_gis.admin.mode, "Expected admin mode property to be available after reconnect"
        assert reconnected_gis.admin.mode.get('isReadOnly') is True, "Expected read only mode to be True after reconnect"

        self.gis.admin.mode = None
        assert self.gis.admin.mode.get('isReadOnly') is False, "Expected read only mode to be False"


if __name__ == "__main__":
    unittest.main()
