import sys

#
#  Update the Path to set the test area
sys.path.insert(0, r"c:\SVN\geosaurus_master\src")
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


class Test_PortalAdmin(unittest.TestCase):
    def test_info_11_1(self):
        username = "PAPIadmin"
        password = "PAPIletmein01"
        gis = GIS(
            url="https://rpubs22101.ags.esri.com/portal",
            username=username,
            password=password,
            proxy=PROXIES,
            verify_cert=False,
        )
        assert gis.admin.info

    def test_info_pre_11_1(self):

        gis = GIS(
            profile=profiles[0],
            proxy=PROXIES,
            verify_cert=False,
        )
        assert gis.admin.info is None


if __name__ == "__main__":
    unittest.main()
