import unittest
from arcgis.gis import GIS
from arcgis.auth import EsriAPIKeyAuth, EsriSession, EsriKerberosAuth
from utils.decorators import credentials, integration_test


@credentials.agol_api_key
@integration_test
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
            assert data.get("appInfo", {'DEFAULT_KEY':'DEFAULT_VALUE'})
            assert not "user" in data

    def test_api_key_gis(self):
        gis = GIS(url=self.portal_url, api_key=self.password)
        assert gis._con._auth == "API_KEY"
        assert gis.properties.get("appInfo", {}).get("appOwner", 'DEFAULT_OWNER')


if __name__ == "__main__":
    unittest.main()
