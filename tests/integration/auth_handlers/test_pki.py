import sys

sys.path.insert(0, r"C:\SVN\geosaurus_master\src")
sys.path.insert(1, r"C:\SVN\geosaurus_master\tests")
import os
import tempfile
import unittest
from arcgis.auth import EsriWindowsAuth, EsriSession
from arcgis.auth.tools import pfx_to_pem

verify_cert = False
trust_env = True

try:
    from _config_utils import get_config_parser
except:
    from ._config_utils import get_config_parser

if "pki" in get_config_parser():
    url_pki = get_config_parser()["pki"]["url"]
    password = get_config_parser()["pki"]["password"]
    cert_url = get_config_parser()["pki"]["cert"]
    SKIPME = False
    msg = "all good"
else:
    SKIPME = True
    msg = "Configuration file not found."

try:
    cert_file = cert_url
    if os.path.isfile(cert_file):
        SKIP = False
        msg = "all good"
    else:
        SKIP = True
        msg = "COULD NOT DOWNLOAD THE PKI CERTIFICATE"
except:
    SKIP = True
    msg = "COULD NOT DOWNLOAD THE PKI CERTIFICATE"

from utils.decorators import integration_test


@unittest.skipIf(SKIP or SKIPME, msg)
@integration_test
class TestPKISession(unittest.TestCase):
    """Tests the PKI Security on Enterprise Configuration"""

    def test_simple_pfx_to_pem(self):
        values = pfx_to_pem(
            pfx_path=cert_file,
            pfx_password=password,
            folder=tempfile.gettempdir(),
        )
        assert values
        [os.remove(f) for f in values]

    def test_simple_pfx_to_pem(self):
        values = pfx_to_pem(pfx_path=cert_file, pfx_password=password)
        assert values
        [os.remove(f) for f in values]

    def test_simple_login_pure_requests(self):
        values = pfx_to_pem(pfx_path=cert_file, pfx_password=password)
        import requests

        s = requests.Session()
        s.verify = False
        s.cert = values
        resp = s.get(
            url=f"{url_pki}/sharing/rest/portals/self/servers?f=json"
        )
        assert resp.text
        [os.remove(f) for f in values]

    def test_simple_login_esri_session(self):
        values = pfx_to_pem(pfx_path=cert_file, pfx_password=password)
        with EsriSession(cert=values, verify_cert=False) as session:
            assert session.get(
                f"{url_pki}/sharing/rest/portals/self/servers?f=json"
            ).text
        [os.remove(f) for f in values]

    def test_simple_login_multi_auth(self):
        values = pfx_to_pem(pfx_path=cert_file, pfx_password=password)
        extra_auth = EsriWindowsAuth()
        with EsriSession(
            cert=values, verify_cert=False, auth=extra_auth
        ) as session:
            assert session.get(
                f"{url_pki}/sharing/rest/portals/self/servers?f=json"
            ).text
        [os.remove(f) for f in values]

    def test_simple_login_server_test(self):
        values = pfx_to_pem(pfx_path=cert_file, pfx_password=password)
        with EsriSession(cert=values, verify_cert=False) as session:
            assert session.get(
                f"{url_pki}/sharing/rest/portals/self/servers?f=json"
            ).text
        [os.remove(f) for f in values]


if __name__ == "__main__":
    unittest.main()
