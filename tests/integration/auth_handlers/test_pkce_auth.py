import unittest
from arcgis.auth import EsriPKCEAuth, EsriSession
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.enterprise_and_agol
@integration_test
class TestPkceAuthHandler(unittest.TestCase):
    def test_esri_session(self):
        """tests the esri session auth"""
        gis = self.gis
        username, password, url = gis._username, gis._password, gis.url
        auth = EsriPKCEAuth(url, username, password)
        with EsriSession(
            auth=auth, proxies=self.proxies, verify_cert=False
        ) as session:
            data = session.get(
                f"{url}/sharing/rest/portals/self?f=json"
            ).json()
            assert (
                data.get("user", {}).get("username", "").lower()
                == username.lower()
            )

    def test_gis(self):
        """tests the PKCE auth on AGOL using a GIS"""
        gis = self.gis
        username, password, url = gis._username, gis._password, gis.url
        del gis

        auth = EsriPKCEAuth(url, username, password)
        gis = GIS(url=url, custom_auth=auth)
        assert gis.users.me
        assert gis.users.me.username
        assert gis.users.me.username.lower() == username.lower()
        del gis


if __name__ == "__main__":
    unittest.main()
