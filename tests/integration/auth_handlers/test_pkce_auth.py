import sys

#
#  Update the Path to set the test area
sys.path.insert(0, r"C:\SVN\geosaurus_master_issue_8966\src")
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile', 'your_enterprise_profile']

PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


class Test_PKCEAuthHandler(unittest.TestCase):
    def test_esri_session_enterprise(self):
        """tests the esri session auth on enterprise"""
        from arcgis.auth import EsriSession
        from arcgis.auth import EsriPKCEAuth

        gis = GIS(
            profile=profiles[1],
            verify_cert=False,
            proxy=PROXIES,
        )
        username, password, url = gis._username, gis._password, gis.url
        auth = EsriPKCEAuth(url, username, password)
        with EsriSession(auth=auth, proxies=PROXIES, verify_cert=False) as session:
            purl = f"{url}/sharing/rest/portals/self?f=json"
            data = session.get(purl).json()
            assert data['user']['username'].lower() == username.lower()

    def test_esri_session_agol(self):
        """tests the esri session auth on AGOL"""
        gis = GIS(
            profile=profiles[0],
            verify_cert=False,
            proxy=PROXIES,
        )
        username, password, url = gis._username, gis._password, gis.url
        del gis
        from arcgis.auth import EsriSession
        from arcgis.auth import EsriPKCEAuth

        auth = EsriPKCEAuth(url, username, password)
        with EsriSession(auth=auth) as session:
            purl = f"{url}/sharing/rest/portals/self?f=json"
            data = session.get(purl).json()
            assert data['user']['username'].lower() == username.lower()

    def test_gis_agol(self):
        """tests the PKCE auth on AGOL using a GIS"""
        gis = GIS(
            profile=profiles[0],
            verify_cert=False,
            proxy=PROXIES,
        )
        username, password, url = gis._username, gis._password, gis.url
        del gis
        from arcgis.auth import EsriSession
        from arcgis.auth import EsriPKCEAuth

        auth = EsriPKCEAuth(url, username, password)
        gis = GIS(url=url, custom_auth=auth)
        assert gis.users.me.username.lower() == username.lower()
        del gis


if __name__ == "__main__":
    unittest.main()
