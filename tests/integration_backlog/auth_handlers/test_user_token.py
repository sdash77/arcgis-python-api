import unittest
from arcgis.auth import EsriSession, EsriUserTokenAuth, EsriBuiltInAuth
from utils.decorators import credentials, integration_test

@credentials.enterprise
@integration_test
class TestUserToken(unittest.TestCase):
    def setUp(self):
        self.auth_handler = EsriBuiltInAuth(
            self.portal_url,
            self.username,
            self.password,
        )

    def test_user_token_test(self):
        """user token tests"""
        builtin = self.auth_handler
        user_token = builtin.token
        referer = builtin._referer
        token_auth = EsriUserTokenAuth(
            token=user_token, referer=referer, verify_cert=True, legacy=False
        )
        with EsriSession(auth=token_auth) as session:
            url = f"{self.portal_url}/sharing/rest/portals/self/servers?f=json"
            data = session.get(url).json()
            assert data["servers"]
        token_auth = EsriUserTokenAuth(
            token=user_token, referer=referer, verify_cert=True, legacy=True
        )
        with EsriSession(auth=token_auth) as session:
            url = f"{self.portal_url}/sharing/rest/portals/self/servers?f=json"
            data = session.get(url).json()
            assert data["servers"]
            data = session.post(url).json()
            assert data["servers"]
            with self.assertRaises(Exception):
                data = session.put(url)

    def test_user_token_invalid_token(self):
        builtin = self.auth_handler
        user_token = builtin.token
        referer = builtin._referer
        token_auth = EsriUserTokenAuth(
            token=user_token, referer=referer, verify_cert=True, legacy=False
        )
        with EsriSession(auth=token_auth) as session:
            url = "https://www.arcgis.com/sharing/rest/portals/self?f=json"
            data = session.get(url).json()
            assert data.get("user", False) == False
            data = session.get(url).json()
            assert data.get("user", False) == False


if __name__ == "__main__":
    unittest.main()
