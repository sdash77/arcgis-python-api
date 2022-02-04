import sys

sys.path.insert(0, r"c:\SVN\geosaurus_master_issue_4790a\src")
import unittest


try:
    from _utils import get_config_parser
except:
    from ._utils import get_config_parser

from arcgis.gis import GIS

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
        gis = GIS(url=base_url, client_id=client_id)
        print(gis.properties)

    def test_client_id_client_secret(self):
        """
        Tests the client/secret workflow
        """

        gis = GIS(
            url=base_url,
            client_id=client_id,
            client_secret=client_secret,
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
        )

        assert gis.properties["appInfo"]["appOwner"]


if __name__ == "__main__":
    unittest.main()
