import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

from arcgis.gis.kubernetes._admin._system import EnterpriseFunctions

PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging()


@integration_test
@profiles.admin_devent
class Test_EnterpriseFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._gis = cls.gis

    def test_property(self):
        gis = self._gis
        ef = gis.admin.system.enterprise_functions
        assert isinstance(ef, EnterpriseFunctions)
    
    def test_enterprise_functions_properties(self):
        gis = self._gis
        ef = gis.admin.system.enterprise_functions
        assert isinstance(ef.enabled_functions, list)
        assert isinstance(ef.licensed, list)
    
    def test_enable_disable(self):
        gis = self._gis
        ef = gis.admin.system.enterprise_functions
        lic: str = None
        for available_license in ef.licensed:
            if not available_license in ef.enabled_functions:
                lic = available_license
                break
        if lic:
            response = ef.enable(lic)
            assert response
            assert ef.disable(lic)
        else:
            self.skipTest("No functionality licenses are available for the test.")
    
    


if __name__ == "__main__":
    unittest.main()
