import os
import tempfile
import unittest
from arcgis.auth import EsriWindowsAuth, EsriSession
from arcgis.auth.tools import pfx_to_pem

from utils.decorators import integration_test, credentials


@integration_test
@credentials.enterprise_pki
class TestPKISession(unittest.TestCase):
    """Tests the PKI Security on Enterprise Configuration"""

    def test_simple_pfx_to_pem_specifies_output_folder(self):
        values = pfx_to_pem(
            pfx_path=self.cert,
            pfx_password=self.password,
            folder=tempfile.gettempdir(),
        )
        assert values
        assert len(values) == 2
        assert os.path.exists(values[0])
        assert os.path.exists(values[1])

    def test_simple_pfx_to_pem(self):
        values = pfx_to_pem(pfx_path=self.cert, pfx_password=self.password)
        assert values
        assert len(values) == 2
        assert os.path.exists(values[0])
        assert os.path.exists(values[1])

    def test_simple_login_pure_requests(self):
        values = pfx_to_pem(pfx_path=self.cert, pfx_password=self.password)
        import requests

        s = requests.Session()
        s.verify = False
        s.cert = values
        resp = s.get(url=f"{self.portal_url}/sharing/rest/portals/self/servers?f=json")
        assert resp.ok
        assert resp.json()
        assert resp.json().get("servers")

    def test_simple_login_esri_session(self):
        values = pfx_to_pem(pfx_path=self.cert, pfx_password=self.password)
        with EsriSession(cert=values, verify_cert=False) as session:
            resp = session.get(
                f"{self.portal_url}/sharing/rest/portals/self/servers?f=json"
            )
            assert resp.ok
            assert resp.json()
            assert resp.json().get("servers")

    def test_simple_login_multi_auth(self):
        values = pfx_to_pem(pfx_path=self.cert, pfx_password=self.password)
        extra_auth = EsriWindowsAuth()
        with EsriSession(cert=values, verify_cert=False, auth=extra_auth) as session:
            resp = session.get(
                f"{self.portal_url}/sharing/rest/portals/self/servers?f=json"
            )
            assert resp.ok
            assert resp.json()
            assert resp.json().get("servers")

    def test_simple_login_server_test(self):
        values = pfx_to_pem(pfx_path=self.cert, pfx_password=self.password)
        with EsriSession(cert=values, verify_cert=False) as session:
            resp = session.get(
                f"{self.portal_url}/sharing/rest/portals/self/servers?f=json"
            )
            assert resp.ok
            assert resp.json()
            assert resp.json().get("servers")


if __name__ == "__main__":
    unittest.main()
