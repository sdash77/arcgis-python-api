import sys

sys.path.insert(0, r"c:\SVN\geosaurus_master\src")
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
    base_url = "https://datasciencedev.esri.com/portal"  # get_config_parser()["oauth"]["base_url"]
    client_id = "HkaOom5nPxZxegLu"  # get_config_parser()["oauth"]["client_id"]
    client_secret = "1d773c803794496bbb0bf16a5696cd2e"  # get_config_parser()["oauth"]["client_secret"]
    username = "portaladmin"  # get_config_parser()["oauth"]["username"]
    password = "esri.agp"  # get_config_parser()["oauth"]["password"]
    SKIPME = False
    msg = "all good"
else:
    SKIPME = True
    msg = "Configuration file not found."


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
            url=base_url, client_id=client_id, verify_cert=VERIFY_CERT, proxy=PROXIES
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


if __name__ == "__main__":
    unittest.main()
