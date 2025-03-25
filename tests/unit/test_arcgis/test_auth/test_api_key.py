import unittest
from arcgis.auth import EsriAPIKeyAuth, EsriKerberosAuth, EsriSession

class TestApiKey(unittest.TestCase):
    """Tests working with the API Key"""

    def setUp(self):
        self.password = "NOT_A_REAL_API_KEY"
        self.session =  EsriSession()
        self.api_key_handler = EsriAPIKeyAuth(
            api_key=self.password, referer=""
        )
        self.referer = "AmazingEsri"
        self.api_key_handler_referer = EsriAPIKeyAuth(
            api_key=self.password, referer=self.referer
        )
        self.api_key_handler_kerberos = EsriAPIKeyAuth(
            api_key=self.password, auth=EsriKerberosAuth(referer="", session=self.session)
        )

    def test_api_key(self):
        auth = self.api_key_handler
        api_key = self.password
        assert auth.api_key == api_key
        assert auth.referer == ""
        assert auth.verify_cert in (True, False)
        assert auth.token == api_key

    def test_token_property(self):
        auth = self.api_key_handler
        api_key = self.password
        assert auth.token == api_key
        auth.token = "THIS IS NOT RIGHT"
        assert auth.token != api_key
        assert auth.token == "THIS IS NOT RIGHT"

    def test_api_key_referer(self):
        assert self.api_key_handler_referer.referer == self.referer

    def test_api_key_auth(self):
        auth = self.api_key_handler_kerberos
        assert auth.auth
        assert isinstance(auth.auth, EsriKerberosAuth)


if __name__ == "__main__":
    unittest.main()
