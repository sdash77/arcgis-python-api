import os
import tempfile
import unittest
from arcgis.auth import EsriWindowsAuth, EsriSession
from arcgis.auth.tools import pfx_to_pem
import requests_negotiate_sspi
from arcgis.gis import GIS

verify_cert = False
trust_env = True

try:
    from _utils import get_config_parser
except:
    from ._utils import get_config_parser

if "pki" in get_config_parser():
    url_pki = get_config_parser()['pki']['url']
    password = get_config_parser()["pki"]["password"]
    cert_url = get_config_parser()["pki"]["cert"]
    SKIPME = False
    msg = "all good"
else:
    SKIPME = True
    msg = "Configuration file not found."

try:
    import requests

    resp = requests.get(
        cert_url, auth=requests_negotiate_sspi.HttpNegotiateAuth()
    )
    if resp.headers["content-type"] == "text/html":
        1 / 0
    data = resp.content
    cert_file = r"./gisproadv1.pfx"
    with open(cert_file, "wb") as writer:
        writer.write(data)
    SKIP = False
    msg = "all good"
except:
    SKIP = True
    msg = "COULD NOT DOWNLOAD THE PKI CERTIFICATE"


from utils.decorators import integration_test


@integration_test
@unittest.skipIf(SKIP or SKIPME, msg)
class TestPKISession(unittest.TestCase):
    """Tests the PKI Security on Enterprise Configuration"""

    def test_simple_login_pki(self):
        cert_file, key_file = pfx_to_pem(
            pfx_path="./gisproadv1.pfx", pfx_password=password
        )
        gis = GIS(url_pki, cert_file=cert_file, key_file=key_file)
        assert gis.users.me


if __name__ == "__main__":
    unittest.main()
