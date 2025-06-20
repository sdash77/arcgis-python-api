import sys
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
    root.addHandler(handler)


server_urls = {
    "IWA": "https://rqawiniwasasv.ags.esri.com/gis/rest/services",
    "BUILT-IN-LINUX": "https://rqalnxbisasv.esri.com/gis",
}
BUILTIN = ('creator2', "portalaccount1")
PROXIES = detect_proxy(True)  # Handles Fiddler when True

enable_verbose_logging(__logger__)

from arcgis.gis.server.catalog import ServicesDirectory


@integration_test
class Test_ServiceDirectoryLogins(unittest.TestCase):
    def test_iwa(self):
        sd = ServicesDirectory(
            url=server_urls['IWA'],
            proxy=detect_proxy(True),
        )
        assert sd.properties

    def test_built_in_auth_trailing_forward_slash(self):
        sd = ServicesDirectory(
            url=server_urls['BUILT-IN-LINUX'] + "/",
            username=BUILTIN[0],
            password=BUILTIN[1],
            proxy=detect_proxy(True),
        )
        assert sd.properties

    def test_built_in_auth(self):
        sd = ServicesDirectory(
            url=server_urls['BUILT-IN-LINUX'],
            username=BUILTIN[0],
            password=BUILTIN[1],
            proxy=detect_proxy(True),
        )
        assert sd.properties


if __name__ == "__main__":
    unittest.main()
