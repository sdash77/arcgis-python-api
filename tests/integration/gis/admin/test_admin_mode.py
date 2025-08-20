import unittest
from utils._logging import enable_verbose_logging
from utils.decorators import integration_test, profiles

import arcgis

enable_verbose_logging()


@unittest.skip("Manual test, comment this decorator to run")
@profiles.admin_enterprise_and_k8s
@integration_test
class TestMode(unittest.TestCase):
    
    def test_set_readonly(self):
        """tests setting the portal to read only mode"""
        assert self.gis
        assert self.gis.users.me
        if not self.gis._is_kubernetes:
            self.gis.admin.mode = {'read_only': True}
            assert self.gis.admin.mode
        else:
            self.gis.admin.mode.update(
               read_only=True,
               description="ArcGIS Kubernetes deployment now in read-only mode."
            )
            assert self.gis.admin.mode
        reconnected_gis = arcgis.gis.GIS(profile=self.profile, proxy=self.proxies, verify_cert=False)
        if not reconnected_gis._is_kubernetes:
            assert self.gis.admin.mode.get('isReadOnly') is True, "Expected read only mode to be True"
            self.gis.admin.mode = {'read_only': False}
        else:
            assert reconnected_gis.admin.mode.read_only.get("isReadOnly") is True, "Expected read-only mode to be True"
            self.gis.admin.mode.update(
                read_only=False,
                description="ArcGIS Kubernetes deployment now in editable mode."
            )
            
    def test_set_readonly_reconnect(self):
        """tests setting the portal to read only mode, checking reconnect"""
        assert self.gis, "Expected GIS object to be available"
        assert self.gis.users.me, "Expected authenticated user to be available"
        if not self.gis._is_kubernetes:
            self.gis.admin.mode = {'read_only': True}
            assert self.gis.admin.mode
        else:
            self.gis.admin.mode.update(
                read_only=True,
                description="ArcGIS Kubernetes deployment in read-only mode."
            )
            assert self.gis.admin.mode           
        reconnected_gis = arcgis.gis.GIS(profile=self.profile, proxy=self.proxies, verify_cert=False)
        assert reconnected_gis.users.me
        assert reconnected_gis.admin, "Expected admin property to be available after reconnect"
        assert reconnected_gis.admin.mode, "Expected admin mode property or method to be available after reconnect"
        if not self.gis._is_kubernetes:
            assert reconnected_gis.admin.mode.get('isReadOnly') is True, "Expected read only mode to be True after reconnect"
            self.gis.admin.mode = None         
        else:
            assert reconnected_gis.admin.mode.read_only.get('isReadOnly') is True, "Expected read only mode to be True after reconnect."
            self.gis.admin.mode.update(
                read_only=False,
                description="ArcGIS Kubernetes deployment in editable mode."
            )
        final_connect = arcgis.gis.GIS(profile=self.profile, proxy=self.proxies, verify_cert=False)
        if not final_connect._is_kubernetes:
            assert final_connect.admin.mode.get('isReadOnly') is False, "Expected read-only to be False."
        else:
            assert final_connect.admin.mode.read_only.get('isReadOnly') is False, "Expected read-only to be False."


if __name__ == "__main__":
    unittest.main()
