import unittest


try:
    from _utils import get_config_parser
except:
    from ._utils import get_config_parser
import arcgis

print(arcgis.__file__)
from arcgis.gis import GIS
from arcgis.auth.tools._util import detect_proxy

PROXIES = detect_proxy(True)
VERIFY_CERT = False
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

if "oauth" in get_config_parser():
    base_agol_url = None
    ago_client_id = get_config_parser()["oauth_agol"]["client_id"]

    ago_client_secret = get_config_parser()["oauth_agol"]["client_secret"]
    ago_username = get_config_parser()["oauth_agol"]["username"]
    ago_password = get_config_parser()["oauth_agol"]["password"]
    ago_SKIPME = False
    ago_msg = "all good"
else:
    ago_SKIPME = True
    ago_msg = "Configuration file not found."


from utils.decorators import integration_test


@integration_test
@unittest.skipIf(SKIPME == True, msg)
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
            url=base_url,
            client_id=client_id,
            verify_cert=VERIFY_CERT,
            proxy=PROXIES,
        )
        print(gis.properties)

    def test_client_id_client_secret(self):
        """
        Tests the client/secret workflow
        """

        gis = GIS(
            url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            verify_cert=VERIFY_CERT,
            proxy=PROXIES,
        )
        assert gis.properties["appInfo"]["appOwner"]

    def test_client_id_username_pw(self):
        """
        Tests the client + username/password provided workflow
        """

        gis = GIS(
            url=base_url,
            client_id=client_id,
            username=username,
            password=password,
            verify_cert=VERIFY_CERT,
            proxy=PROXIES,
        )

        assert gis.properties["appInfo"]["appOwner"]

    def test_client_id_client_secret_username_pw(self):
        """
        Tests the client/secret + username/password provided workflow
        """
        gis = GIS(
            url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            verify_cert=VERIFY_CERT,
            proxy=PROXIES,
        )

        assert gis.properties["appInfo"]["appOwner"]


@unittest.skipIf(SKIPME == True, msg)
class TestOAuth2WorkflowAGOL(unittest.TestCase):
    """
    Tests the Oauth2 Token Authentication Workflows
    """

    @unittest.skip(reason="manual process")
    def test_client_id_only(self):
        """
        Tests the manual workflow for the client_id only workflow
        """
        gis = GIS(
            url=None,
            client_id=ago_client_id,
            verify_cert=VERIFY_CERT,
            proxy=PROXIES,
        )
        print(gis.properties)

    def test_client_id_client_secret(self):
        """
        Tests the client/secret workflow
        """

        gis = GIS(
            url=None,
            client_id=ago_client_id,
            client_secret=ago_client_secret,
            verify_cert=VERIFY_CERT,
            proxy=PROXIES,
        )
        assert gis.properties["appInfo"]["appOwner"]

    def test_client_id_username_pw(self):
        """
        Tests the client + username/password provided workflow
        """

        gis = GIS(
            url=None,
            client_id=ago_client_id,
            username=ago_username,
            password=ago_password,
            verify_cert=VERIFY_CERT,
            proxy=PROXIES,
        )

        assert gis.properties["appInfo"]["appOwner"]

    def test_client_id_client_secret_username_pw(self):
        """
        Tests the client/secret + username/password provided workflow
        """
        gis = GIS(
            url=None,
            client_id=ago_client_id,
            client_secret=ago_client_secret,
            username=ago_username,
            password=ago_password,
            verify_cert=VERIFY_CERT,
            proxy=PROXIES,
        )

        assert gis.properties["appInfo"]["appOwner"]


if __name__ == "__main__":
    unittest.main()
