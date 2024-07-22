import json, uuid
import unittest

try:
    SKIPME = False
    import requests_mock
except:
    SKIPME = True
from arcgis.auth import EsriSession

from arcgis.auth._auth._token import _parse_arcgis_url

try:
    SKIP_ARCPY = False
    import arcpy

    assert arcpy.GetActivePortalURL()
    assert arcpy.GetSigninToken()
except:
    SKIP_ARCPY = True

mock_resp = json.dumps({"version": "8.3"})
mock_generate_token_url = "https://www.arcgis.com/sharing/generateToken"
mock_portals_self = "https://www.arcgis.com/sharing/rest/portals/self?f=json"
mock_resp_self = json.dumps({"user": {"username": "fakeaccount"}})


mock_generate_token_url = "https://www.arcgis.com/sharing/rest/generateToken"
mock_generate_token_resp = json.dumps(
    {
        "token": "sakjfh97325437hskfsdfd_sdkjfsjf1283763339564921734sdfbdsj",
        "expires": "13472658353687",
    }
)

import unittest
import unittest.mock
from unittest.mock import MagicMock

import arcpy
from arcgis.auth import (
    ArcGISProAuth,
    EsriBuiltInAuth,
    EsriGenTokenAuth,
    EsriUserTokenAuth,
    EsriOAuth2Auth,
    EsriNotebookAuth,
)


@unittest.skipIf(SKIPME, "Missing requests_mock")
class TestURLParseLogic(unittest.TestCase):
    """tests the parse logic for the token url"""

    def test_test_parse_logic(self):
        assert _parse_arcgis_url(url=None) == "https://www.arcgis.com"
        assert (
            _parse_arcgis_url(url="https://www.arcgis.com")
            == "https://www.arcgis.com"
        )
        assert (
            _parse_arcgis_url(url="https://www.arcgis.com/sharing/rest")
            == "https://www.arcgis.com"
        )
        assert (
            _parse_arcgis_url(url="https://www.arcgis.com/sharing")
            == "https://www.arcgis.com"
        )
        assert (
            _parse_arcgis_url(
                url="http://pythonapi.playground.esri.com/portal"
            )
            == "http://pythonapi.playground.esri.com/portal"
        )
        assert (
            _parse_arcgis_url(
                url="http://pythonapi.playground.esri.com/portal/home"
            )
            == "http://pythonapi.playground.esri.com/portal"
        )
        assert (
            _parse_arcgis_url(
                url="http://pythonapi.playground.esri.com/portal/sharing/rest"
            )
            == "http://pythonapi.playground.esri.com/portal"
        )
        assert (
            _parse_arcgis_url(
                url="http://pythonapi.playground.esri.com/portal/sharing/rest"
            )
            == "http://pythonapi.playground.esri.com/portal"
        )
        assert (
            _parse_arcgis_url(
                url="https://pythonapi.playground.esri.com/portal/sharing/rest"
            )
            == "https://pythonapi.playground.esri.com/portal"
        )


@unittest.skipIf(SKIP_ARCPY, "Issue with ArcPy Settings, Skipping.")
class TestProTokenAuth(unittest.TestCase):
    """
    Tests the EsriSession Pro Token Auth
    """

    @unittest.skipIf(SKIPME, "Missing requests_mock")
    def test_token(self):
        auth = ArcGISProAuth()
        assert auth.token


@unittest.skipIf(SKIPME, "Missing requests_mock")
class TestArcGISTokenAuth(unittest.TestCase):
    """
    Tests the EsriSession GenerateToken Auth
    """

    def test_suspend(self):
        username = "gisprostd1"
        password = "portalaccount1"
        builtin = EsriBuiltInAuth(
            "https://rqawinbi01pt.ags.esri.com/gis", username, password
        )
        with EsriSession(auth=builtin) as session:
            resp = session.get(
                "https://rqawinbi01pt.ags.esri.com/gis/sharing/rest/portals/self?f=json"
            )
            data = resp.json()
            assert data["user"]["username"] == username
        assert builtin.suspend()

    def test_get_auth_no_auth(self):
        """tests the workflow to use a token then a call to where the token is not valid to"""

        from arcgis.auth import EsriBuiltInAuth

        username = "esri_requests"
        password = "portalaccount1"
        auth = EsriBuiltInAuth(
            url="https://pythonapi.playground.esri.com/portal",
            username=username,
            password=password,
            verify_cert=False,
        )
        with EsriSession(auth=auth, verify_cert=False) as session:
            data = session.post(
                url="https://www.arcgis.com/sharing/rest/search",
                data={"f": "json", "q": "map"},
            ).json()
            assert "results" in data
        session.close()

    def test_oauth_builtin_questions_not_set(self):
        """ """
        username = "esri_requests"
        password = "portalaccount1"
        from arcgis.auth import EsriBuiltInAuth

        auth = EsriBuiltInAuth(
            url="https://pythonapi.playground.esri.com/portal",
            username=username,
            password=password,
            verify_cert=False,
        )
        assert auth.token

    def test_oauth_builtin_invalid_user(self):
        """
        Ensures the Auth handler workflow fails and error is raised.
        """
        url = "https://pythonapi.playground.esri.com/portal"
        with self.assertRaises(Exception) as context:
            from arcgis.auth import EsriBuiltInAuth

            auth = EsriBuiltInAuth(
                url=url,
                username="FakeAccountDNE",
                password="terrible.password1",
                verify_cert=False,
            )
            auth.token


class TestUserTokenAuth(unittest.TestCase):
    """
    Tests the EsriSession GenerateToken Auth
    """

    def test_user_provided_token(self):
        """tests the userprovided token workflow"""

        username = "esri_requests"
        password = "portalaccount1"
        client_id = "N7JHmMBPdYo2xpSY"
        client_secret = "9759bf23f310496685bd36f255b7a499"
        client_oauth = EsriOAuth2Auth(
            base_url="https://pythonapi.playground.esri.com/portal/sharing/rest",
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
        )

        user_token_auth = EsriUserTokenAuth(
            token=client_oauth._oauth_token(), referer=client_oauth._referer
        )
        with EsriSession(auth=user_token_auth, retries=10) as session:
            resp = session.get(
                "https://pythonapi.playground.esri.com/portal/sharing/rest/portals/self?f=json"
            )
            data = resp.json()
            assert data["appInfo"]["appOwner"]


class TestEsriNotebookAuth(unittest.TestCase):
    def test_notebook(self):
        username = "esri_requests"
        password = "portalaccount1"
        client_id = "N7JHmMBPdYo2xpSY"
        client_secret = "9759bf23f310496685bd36f255b7a499"
        client_oauth = EsriOAuth2Auth(
            base_url="https://pythonapi.playground.esri.com/portal/sharing/rest",
            client_id=client_id,
            client_secret=client_secret,
            referer="",
            username=username,
            password=password,
        )

        user_token_auth = EsriNotebookAuth(
            token=client_oauth._oauth_token(), referer=client_oauth._referer
        )
        with EsriSession(auth=user_token_auth, referer="") as session:
            resp = session.get(
                "https://pythonapi.playground.esri.com/portal/sharing/rest/portals/self?f=json"
            )
            data = resp.json()
            assert data["appInfo"]["appOwner"]


if __name__ == "__main__":
    unittest.main()
