import sys
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

from utils.decorators import integration_test


@integration_test
class TestMFASecurityAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = "https://devext.arcgis.com/sharing/rest"
        cls.username = "mfauser"
        cls.password = "esri.agp2"
        cls.mfa_code = "QHM72ADVWBPIQHYT"
    
    @unittest.skip("Needs Human Interaction")
    def test_mfa_gis(self):
        from arcgis.gis import GIS
        from arcgis.auth.tools._util import mfa_otp
        url = "https://devext.arcgis.com/sharing/rest"
        username = "mfauser"
        password = "esri.agp2"
        #
        #   Enter the code in twice for the workflow
        #
        verify_code = mfa_otp(self.mfa_code)
        print(verify_code)
        GIS(url=url, username=username, password=password, verify_cert=False, trust_env=True)
        
    
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
            session=EsriSession()
        )
        assert auth.token
    
    def test_login_mfa_call(self):
        
        with EsriSession(
           verify_cert=False, proxy=PROXIES
        ) as session:
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
                session=session, 
            )
            session.auth = auth
            data = session.get(
                "https://devext.arcgis.com/sharing/rest/portals/self?f=json"
            ).json()
            assert data['user']['username'] == "mfauser"


if __name__ == "__main__":
    unittest.main()
