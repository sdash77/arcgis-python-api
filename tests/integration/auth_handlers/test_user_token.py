import sys, json, uuid
import sys

# sys.path.insert(0, r"c:\SVN\geosaurus_master_issue_4790a\src")
import unittest
from arcgis.auth import EsriSession, EsriUserTokenAuth, EsriBuiltInAuth


class TestUserToken(unittest.TestCase):
    def test_user_token_test(self):
        """user token tests"""
        username = "esri_requests"
        password = "portalaccount1"
        builtin = EsriBuiltInAuth(
            "https://pythonapi.playground.esri.com/portal", username, password
        )
        user_token = builtin.token
        referer = builtin._referer
        token_auth = EsriUserTokenAuth(
            token=user_token, referer=referer, verify_cert=True, legacy=False
        )
        with EsriSession(auth=token_auth) as session:
            url = "https://pythonapi.playground.esri.com/portal/sharing/rest/portals/self/servers?f=json"
            data = session.get(url).json()
            assert data["servers"]
        token_auth = EsriUserTokenAuth(
            token=user_token, referer=referer, verify_cert=True, legacy=True
        )
        with EsriSession(auth=token_auth) as session:
            url = "https://pythonapi.playground.esri.com/portal/sharing/rest/portals/self/servers?f=json"
            data = session.get(url).json()
            assert data["servers"]
            data = session.post(url).json()
            assert data["servers"]
            with self.assertRaises(Exception):
                data = session.put(url)

    def test_user_token_invalid_token(self):
        username = "esri_requests"
        password = "portalaccount1"
        builtin = EsriBuiltInAuth(
            "https://pythonapi.playground.esri.com/portal", username, password
        )
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

    def test_none_given(self):
        with self.assertRaises(ValueError):
            token_auth = EsriUserTokenAuth(
                token=None, referer=None, verify_cert=True, legacy=False
            )

    def test_referer_set(self):
        token_auth = EsriUserTokenAuth(
            token="ABCD", referer="ABCD", verify_cert=True, legacy=False
        )
        assert token_auth.referer == "ABCD"


if __name__ == "__main__":
    unittest.main()
