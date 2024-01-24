import unittest
from arcgis.auth import EsriAPIKeyAuth, EsriKerberosAuth
from arcgis.auth._auth._schain import _MultiAuth

class TestMultiAuth(unittest.TestCase):
    def setUp(self):
        self.api_key_handler = EsriAPIKeyAuth(
            api_key="NOT_A_REAL_API_KEY", referer=""
        )

    def test_multi_auth_concat(self):
        """tests using multiple authentication"""
        auth1 = self.api_key_handler + EsriKerberosAuth(referer="")
        auth1 += self.api_key_handler
        auth3 = self.api_key_handler + auth1
        assert auth1
        assert isinstance(auth1, _MultiAuth)
        assert auth3
        assert isinstance(auth3, _MultiAuth)

    def test_multi_auth_and(self):
        """tests using multiple authentication"""
        auth = self.api_key_handler & EsriKerberosAuth(referer="")
        auth2 = self.api_key_handler & auth
        assert auth
        assert isinstance(auth, _MultiAuth)
        assert auth2
        assert isinstance(auth2, _MultiAuth)

if __name__ == "__main__":
    unittest.main()