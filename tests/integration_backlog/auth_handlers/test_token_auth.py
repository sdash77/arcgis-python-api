from arcgis.auth import EsriSession
import unittest

try:
    import arcpy
    HAS_ARCPY = True
except:
    HAS_ARCPY = False

from arcgis.auth import (
    ArcGISProAuth,
    EsriBuiltInAuth,
    EsriUserTokenAuth,
    EsriOAuth2Auth,
    EsriNotebookAuth,
)


@unittest.skipIf(not HAS_ARCPY, "Issue with ArcPy Settings, Skipping.")
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
