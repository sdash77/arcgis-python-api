import unittest
from arcgis.gis import GIS
from arcgis.auth.tools._util import detect_proxy

PROXIES = detect_proxy(True)
VERIFY_CERT = False

from utils.decorators import credentials, integration_test

@integration_test
@credentials.all_oauth
class TestOAuth2Workflow(unittest.TestCase):
    """
    Tests the Oauth2 Token Authentication Workflows
    """

    @unittest.skip(reason="manual process")
    def test_client_id_only(self):
        """
        Tests the manual workflow for the client_id only workflow
        """
        gis = GIS(
            url=self.portal_url,
            client_id=self.client_id,
            verify_cert=VERIFY_CERT,
            proxy=PROXIES,
        )
        print(gis.properties)

    def test_client_id_client_secret(self):
        """
        Tests the client/secret workflow
        """

        gis = GIS(
            url=self.portal_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            verify_cert=VERIFY_CERT,
            proxy=PROXIES,
        )
        assert gis.properties.get("appInfo", {}).get("appOwner")

    def test_client_id_username_pw(self):
        """
        Tests the client + username/password provided workflow
        """

        gis = GIS(
            url=self.portal_url,
            client_id=self.client_id,
            username=self.username,
            password=self.password,
            verify_cert=VERIFY_CERT,
            proxy=PROXIES,
        )
        assert gis.properties.get("appInfo", {}).get("appOwner")

    def test_client_id_client_secret_username_pw(self):
        """
        Tests the client/secret + username/password provided workflow
        """
        gis = GIS(
            url=self.portal_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            password=self.password,
            verify_cert=VERIFY_CERT,
            proxy=PROXIES,
        )
        assert gis.properties.get("appInfo", {}).get("appOwner")

if __name__ == "__main__":
    unittest.main()
