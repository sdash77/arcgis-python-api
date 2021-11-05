import sys, os

sys.path.insert(0, r"c:\SVN\geosaurus_master_issue_4790a\src")
import unittest
from arcgis.auth import EsriAPIKeyAuth

try:
    from _utils import get_config_parser
except:
    from ._utils import get_config_parser

from arcgis.gis import GIS

if 'api_key' in get_config_parser():
    SKIPME = False
    SITE_URL = get_config_parser()['api_key']['url']
    API_KEY = get_config_parser()['api_key']['api_key']
else:
    SKIPME = True


@unittest.skipIf(SKIPME, "configuration file not found")
class TestAPIKey(unittest.TestCase):
    """Tests working with the API Key"""

    def test_api_key_login(self):
        gis = GIS(url=SITE_URL, api_key=API_KEY)
        assert gis._con._auth == "USER_TOKEN"
        assert gis.properties['appInfo']['appOwner']


if __name__ == "__main__":
    unittest.main()
