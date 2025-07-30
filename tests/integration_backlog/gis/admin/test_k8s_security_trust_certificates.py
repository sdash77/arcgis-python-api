import sys
import logging
import unittest

from arcgis.gis import GIS
from arcgis.auth.tools._util import detect_proxy
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

enable_verbose_logging()

@profiles.admin_k8s
@integration_test
class TestKubernetesCertificates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis2 = GIS(
            url="https://1130pubbi-1130pubbi.apps.openshift412release.esri.com/web",
            username="PAPIadmin",
            password="PAPIletmein01",
            verify_cert=False,
        )

    def test_trust_certs(self):
        gis = self.gis
        security = gis.admin.security
        
        kubeCert = security.certificates
        assert kubeCert
    
        assert kubeCert.trust_certs
        
        gis2 = self.gis2
        security2 = gis2.admin.security

        kubeCert2 = security2.certificates
        assert kubeCert2
    
        assert kubeCert2.trust_certs        


if __name__ == "__main__":
    unittest.main()
