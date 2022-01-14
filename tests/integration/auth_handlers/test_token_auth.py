import sys, json, uuid

# sys.path.insert(0, r"c:\SVN\geosaurus_master_issue_4790a\src")
import unittest
import requests_mock
from arcgis.auth import EsriSession

from arcgis.auth._auth._token import _parse_arcgis_url

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


class ArcPyMock(object):
    """mocking the arcpy module"""

    @staticmethod
    def GetActivePortalURL(*args, **kwargs):
        return "https://www.arcgis.com/sharing/rest"

    @staticmethod
    def GetSigninToken(*args, **kwargs):
        return {"token": "abcd1234", "referer": "arcpymock"}


sys.modules["arcpy"] = ArcPyMock()
import arcpy
from arcgis.auth import (
    ArcGISProAuth,
    EsriBuiltInAuth,
    EsriGenTokenAuth,
    EsriUserTokenAuth,
    EsriOAuth2Auth,
    EsriNotebookAuth,
)


class TestURLParseLogic(unittest.TestCase):
    """tests the parse logic for the token url"""

    def test_test_parse_logic(self):
        assert _parse_arcgis_url(url=None) == "https://www.arcgis.com"
        assert (
            _parse_arcgis_url(url="https://www.arcgis.com") == "https://www.arcgis.com"
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
            _parse_arcgis_url(url="http://pythonapi.playground.esri.com/portal")
            == "http://pythonapi.playground.esri.com/portal"
        )
        assert (
            _parse_arcgis_url(url="http://pythonapi.playground.esri.com/portal/home")
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


@unittest.skip('i want to')
class TestGenerateTokenAuth(unittest.TestCase):
    """
    Tests the EsriSession GenerateToken Auth
    """

    def test_generate_token(self):
        """tests the generate token"""
        with requests_mock.Mocker() as m:
            m.post(mock_generate_token_url, text=mock_generate_token_resp)
            m.get(mock_generate_token_url, text=mock_generate_token_resp)
            auth = EsriGenTokenAuth(
                token_url=mock_generate_token_url,
                referer="http",
                username="fakeaccount",
                password="password_fake",
            )
            self.assertEqual(
                auth.token(),
                "sakjfh97325437hskfsdfd_sdkjfsjf1283763339564921734sdfbdsj",
            )
            auth = EsriGenTokenAuth(
                token_url=mock_generate_token_url,
                referer="http",
                username="fakeaccount",
                password="password_fake",
            )
            auth2 = EsriGenTokenAuth(
                token_url=mock_generate_token_url, referer="http", portal_auth=auth
            )
            self.assertEqual(
                auth2.token("https://fake/test.com"),
                "sakjfh97325437hskfsdfd_sdkjfsjf1283763339564921734sdfbdsj",
            )


@unittest.mock.patch(target="__main__.arcpy", new=ArcPyMock, create=True)
class TestProTokenAuth(unittest.TestCase):
    """
    Tests the EsriSession Pro Token Auth
    """

    def test_token(self):
        auth = ArcGISProAuth()
        assert auth.token


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
        """tests the workflow to use a token then a call to where the token is not valid to """

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
        """

        """
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
        with self.assertRaises(ValueError) as context:
            from arcgis.auth import EsriBuiltInAuth

            auth = EsriBuiltInAuth(
                url=url,
                username="FakeAccountDNE",
                password='terrible.password1',
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
