import sys
import logging
import unittest

from arcgis.gis import GIS
from arcgis.auth.tools._util import detect_proxy
from utils.decorators import integration_test, profiles

__logger__ = logging.getLogger()

def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)
    
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

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
            proxy=PROXIES
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
