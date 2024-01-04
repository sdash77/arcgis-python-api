import unittest
from arcgis.auth import EsriAPIKeyAuth, EsriSession, EsriKerberosAuth
from utils.decorators.cls import agol_api_key_only


@agol_api_key_only
class TestApiKey(unittest.TestCase):
    """Tests working with the API Key"""

    def setUp(self):
        self.api_key_handler = EsriAPIKeyAuth(
            api_key=self.password, auth=EsriKerberosAuth(referer="")
        )

    def test_api_key_op(self):
        """Tests a web call using a API Key"""
        auth = self.api_key_handler
        with EsriSession(auth=auth) as session:
            resp = session.get(
                url=f"{self.portal_url}/sharing/rest/portals/self?f=json"
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "appInfo" in data
            assert not "user" in data


if __name__ == "__main__":
    unittest.main()
