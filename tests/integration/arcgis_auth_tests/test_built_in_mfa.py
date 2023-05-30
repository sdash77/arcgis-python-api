import sys

#
#  Update the Path to set the test area
# sys.path.insert(0, r"C:\SVN\geosaurus_master\src")
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.auth import EsriSession, EsriBuiltInAuth
from arcgis.auth.tools._util import mfa_otp
from arcgis.gis import GIS

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)


PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


class TestMFASecurityAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = "https://devext.arcgis.com/sharing/rest"
        cls.username = "mfauser"
        cls.password = "esri.agp2"
        cls.mfa_code = "WTE74DJZEHX2ZWVW"

    def test_login_mfa(self):
        auth = EsriBuiltInAuth(
            url=self.url,
            username=self.username,
            password=self.password,
            expiration=None,
            legacy=False,
            verify_cert=False,
            referer=None,
            proxies=PROXIES,
            mfa_code=self.mfa_code,
        )
        assert auth.token

    def test_login_mfa_call(self):
        auth = EsriBuiltInAuth(
            url=self.url,
            username=self.username,
            password=self.password,
            expiration=None,
            legacy=False,
            verify_cert=False,
            referer=None,
            proxies=PROXIES,
            mfa_code=self.mfa_code,
        )
        with EsriSession(
            auth=auth, verify_cert=False, proxy=PROXIES
        ) as session:
            data = session.get(
                "https://devext.arcgis.com/sharing/rest/portals/self?f=json"
            ).json()
            assert data['user']['username'] == "mfauser"


if __name__ == "__main__":
    unittest.main()
