import sys
import os
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile', 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestGISVerifyCerts(unittest.TestCase):
    def test_verify_boolean_false(self):
        gis = GIS(verify_cert=False)
        assert gis._verify_cert == False

    def test_verify_boolean_true(self):
        gis = GIS(verify_cert=True)
        assert gis._verify_cert == True

    def test_verify_pem(self):
        if os.path.isfile("./cacert.pem"):
            gis = GIS(verify_cert="./cacert.pem")
            assert gis._verify_cert == "./cacert.pem"
        else:
            gis = GIS(verify_cert="./cacert.pem")
            assert gis._verify_cert == True


if __name__ == "__main__":
    unittest.main()
