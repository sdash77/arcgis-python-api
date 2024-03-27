import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis.server import ServicesDirectory
from arcgis.auth import EsriSession
from arcgis.auth._auth._token import ArcGISServerAuth

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

from utils.decorators import integration_test


@integration_test
class TestAGSServerConnectionFile(unittest.TestCase):
    def test_services_directory(self):
        """tests using a services directory with an .ags file"""
        url = "https://rextapilnxsvr01.esri.com/server"
        ags_file = r"./myserver.ags"
        sd = ServicesDirectory(
            url=url,
            ags_file=ags_file,
            proxy=PROXIES,
            verify_cert=False,
        )
        for folder in sd.folders:
            print(sd.list(folder))

    # @unittest.skip("i work")
    def test_requests_session(self):
        """tests the ags connection through the idea"""
        url = "https://rextapilnxsvr01.esri.com/server/rest/services/System"
        with EsriSession(
            auth=ArcGISServerAuth(ags_file=r"./myserver.ags"),
            proxies=PROXIES,
            verify_cert=False,
        ) as session:
            # url = 'https://svinnakota.esri.com/arcgis/rest/services/System'
            resp = session.get(url=url, params={'f': 'json'})
            assert resp.json()
            assert len(resp.json()['services']) > 0


if __name__ == "__main__":
    unittest.main()
