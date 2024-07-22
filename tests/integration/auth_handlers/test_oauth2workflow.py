import unittest

from arcgis.auth import EsriSession
from arcgis.auth import EsriOAuth2Auth

try:
    from _config_utils import get_config_parser
except:
    from ._config_utils import get_config_parser

if "oauth" in get_config_parser():
    base_url = get_config_parser()["oauth"]["base_url"]
    client_id = get_config_parser()["oauth"]["client_id"]
    client_secret = get_config_parser()["oauth"]["client_secret"]
    username = get_config_parser()["oauth"]["username"]
    password = get_config_parser()["oauth"]["password"]
    SKIPME = False
    msg = "all good"
else:
    SKIPME = True
    msg = "Configuration file not found."

from utils.decorators import integration_test


@unittest.skipIf(SKIPME == True, msg)
@integration_test
class TestOAuth2Workflow(unittest.TestCase):
    """
    Tests the Oauth2 Token Authentication Workflows
    """

    @unittest.skip(reason="manual process")
    def test_client_id_only(self):
        """
        Tests the manual workflow for the client_id only workflow
        """
        # client_id = client_id
        client_oauth = EsriOAuth2Auth(
            base_url=base_url,
            client_id=client_id,
        )
        with EsriSession(auth=client_oauth) as session:
            resp = session.get(f"{base_url}/portals/self?f=json")
            data = resp.json()
            assert data["user"]

    def test_client_id_client_secret(self):
        """
        Tests the client/secret workflow
        """

        client_oauth = EsriOAuth2Auth(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
        )
        with EsriSession(auth=client_oauth) as session:
            resp = session.get(f"{base_url}/portals/self?f=json")
            data = resp.json()
            assert data["appInfo"]["appOwner"]

    def test_client_id_username_pw(self):
        """
        Tests the client + username/password provided workflow
        """

        client_oauth = EsriOAuth2Auth(
            base_url=base_url,
            client_id=client_id,
            username=username,
            password=password,
        )
        with EsriSession(auth=client_oauth) as session:
            resp = session.get(f"{base_url}/portals/self?f=json")
            data = resp.json()
            assert data["appInfo"]["appOwner"]

    def test_client_id_client_secret_username_pw(self):
        """
        Tests the client/secret + username/password provided workflow
        """
        client_oauth = EsriOAuth2Auth(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
        )
        with EsriSession(auth=client_oauth) as session:
            resp = session.get(f"{base_url}/portals/self?f=json")
            data = resp.json()
            assert data["appInfo"]["appOwner"]

    def test_refresh_token(self):
        """
        Tests the refresh token operation
        """

        client_oauth = EsriOAuth2Auth(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
        )
        with EsriSession(auth=client_oauth) as session:
            resp = session.get(
                "https://pythonapi.playground.esri.com/portal/sharing/rest/portals/self?f=json"
            )
            data = resp.json()
            assert data["appInfo"]["appOwner"]
            session.auth._token = (
                None  # ensures refresh token case is fired off
            )
            assert session.auth._oauth_token()


if __name__ == "__main__":
    unittest.main()
