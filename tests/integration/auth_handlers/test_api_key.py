import sys, os
import unittest
from arcgis.auth import EsriAPIKeyAuth, EsriSession, EsriKerberosAuth
try:
    from _config_utils import get_config_parser
except:
    from ._config_utils import get_config_parser

    
if 'api_key' in get_config_parser():
    SKIPME = False
    SITE_URL = get_config_parser()['api_key']['url']
    API_KEY = get_config_parser()['api_key']['api_key']
else:
    SKIPME = True

@unittest.skipIf(SKIPME == True, "configuration file not found")
class TestMultiAuth(unittest.TestCase):
    def test_multi_auth(self):
        """tests using multiple authentication"""
        auth1 = EsriAPIKeyAuth(api_key=API_KEY, referer="") + EsriKerberosAuth(
            referer=""
        )
        auth1 += EsriAPIKeyAuth(api_key=API_KEY, referer="")
        auth3 = EsriAPIKeyAuth(api_key=API_KEY, referer="") + auth1
        assert auth1
        assert auth3

    def test_multi_auth_and(self):
        """tests using multiple authentication"""
        auth = EsriAPIKeyAuth(api_key=API_KEY, referer="") & EsriKerberosAuth(
            referer=""
        )
        auth2 = EsriAPIKeyAuth(api_key=API_KEY, referer="") & auth
        assert auth
        assert auth2

@unittest.skipIf(SKIPME, "configuration file not found")
class TestAPIKey(unittest.TestCase):
    """Tests working with the API Key"""

    def test_api_key_login(self):
        auth = EsriAPIKeyAuth(api_key=API_KEY, referer="")
        assert auth.api_key == API_KEY
        assert auth.referer == ""
        assert auth.verify_cert in (True, False)
        assert auth.token == API_KEY

    def test_notebook_get_set(self):
        auth = EsriAPIKeyAuth(api_key=API_KEY, referer="")
        assert auth.token == API_KEY
        auth.token = "THIS IS NOT RIGHT"
        assert auth.token != API_KEY

    def test_api_key_referer(self):
        auth = EsriAPIKeyAuth(api_key=API_KEY, referer="AmazingEsri")
        assert auth.referer == "AmazingEsri"

    def test_api_key_auth(self):
        auth = EsriAPIKeyAuth(
            api_key=API_KEY, referer=None, auth=EsriKerberosAuth(referer="")
        )
        assert auth.auth

    def test_api_key_op(self):
        """Tests a web call using a API Key"""
        auth = EsriAPIKeyAuth(api_key=API_KEY, auth=EsriKerberosAuth(referer=""))
        with EsriSession(auth=auth) as session:
            resp = session.get(url=f"{SITE_URL}/sharing/rest/portals/self?f=json")
            assert resp.status_code == 200
            data = resp.json()
            assert "user" in data or "appInfo" in data
            resp = session.get(
                url=f"https://www.arcgis.com/sharing/rest/portals/self?f=json"
            )
            data = resp.json()
            assert not "user" in data
            resp = session.get(
                url=f"https://www.arcgis.com/sharing/rest/portals/self?f=json"
            )
            data = resp.json()
            assert not "user" in data


if __name__ == "__main__":
    unittest.main()
