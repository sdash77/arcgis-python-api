import unittest
from arcgis.auth import EsriSession
from arcgis.auth import EsriOAuth2Auth
from utils.decorators import integration_test, credentials


@credentials.enterprise_oauth
@integration_test
class TestOAuth2Workflow(unittest.TestCase):
    """
    Tests the Oauth2 Token Authentication Workflows
    """

    @unittest.skip(
        reason="Requires interactive login; launches browser to authenticate"
    )
    def test_client_id_only(self):
        """
        Tests the manual workflow for the client_id only workflow
        """
        sharing_api_url = f"{self.portal_url}/sharing/rest"
        client_oauth = EsriOAuth2Auth(
            base_url=sharing_api_url,
            client_id=self.client_id,
        )
        with EsriSession(auth=client_oauth) as session:
            resp = session.get(f"{sharing_api_url}/portals/self?f=json")
            data = resp.json()
            assert data["user"]

    def test_client_id_client_secret(self):
        """
        Tests the client/secret workflow
        """
        sharing_api_url = f"{self.portal_url}/sharing/rest"
        client_oauth = EsriOAuth2Auth(
            base_url=sharing_api_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        with EsriSession(auth=client_oauth) as session:
            resp = session.get(f"{sharing_api_url}/portals/self?f=json")
            data = resp.json()
            assert data["appInfo"]["appOwner"]

    def test_client_id_username_pw(self):
        """
        Tests the client + username/password provided workflow
        """
        sharing_api_url = f"{self.portal_url}/sharing/rest"
        client_oauth = EsriOAuth2Auth(
            base_url=sharing_api_url,
            client_id=self.client_id,
            username=self.username,
            password=self.password,
        )
        with EsriSession(auth=client_oauth) as session:
            resp = session.get(f"{sharing_api_url}/portals/self?f=json")
            data = resp.json()
            assert data["appInfo"]["appOwner"]

    def test_client_id_client_secret_username_pw(self):
        """
        Tests the client/secret + username/password provided workflow
        """
        sharing_api_url = f"{self.portal_url}/sharing/rest"
        client_oauth = EsriOAuth2Auth(
            base_url=sharing_api_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            password=self.password,
        )
        with EsriSession(auth=client_oauth) as session:
            resp = session.get(f"{sharing_api_url}/portals/self?f=json")
            data = resp.json()
            assert data["appInfo"]["appOwner"]

    def test_refresh_token(self):
        """
        Tests the refresh token operation
        """
        sharing_api_url = f"{self.portal_url}/sharing/rest"
        client_oauth = EsriOAuth2Auth(
            base_url=sharing_api_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            password=self.password,
        )
        with EsriSession(auth=client_oauth) as session:
            resp = session.get(f"{sharing_api_url}/portals/self?f=json")
            data = resp.json()
            assert data["appInfo"]["appOwner"]
            session.auth._token = None  # ensures refresh token case is fired off
            assert session.auth._oauth_token()


if __name__ == "__main__":
    unittest.main()
