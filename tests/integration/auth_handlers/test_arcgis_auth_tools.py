import unittest, os
import requests
from requests import Response
import arcgis.auth

try:
    from _config_utils import get_config_parser
except:
    from ._config_utils import get_config_parser



class TestTools(unittest.TestCase):

    def test_pfx_to_pem(self):
        url = "https://ragsreports.ags.esri.com/information/UserCerts/basic1.pfx"
        pw = "portalaccount1"
        with requests.get(url) as response:
            isinstance(response, Response)
            with open("./basic1.pfx", 'wb') as writer:
                writer.write(response.content)
        k,c = arcgis.auth.tools.pfx_to_pem(pfx_path=r"./basic1.pfx", pfx_password=pw)
        assert all(
            [os.path.isfile(k),
             os.path.isfile(c)]
        )
if __name__ == '__main__':
    unittest.main()