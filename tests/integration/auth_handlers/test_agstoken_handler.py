import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis.server import ServicesDirectory
from arcgis.auth import EsriSession
from arcgis.auth._auth._token import ArcGISServerAuth
from utils.decorators import integration_test
from utils._logging import enable_verbose_logging

try:
    import arcpy

    SKIP = False
except:
    SKIP = True

PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging()


@unittest.skipIf(SKIP, "Requires arcpy; arcpy not available")
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
        assert sd
        for folder in sd.folders:
            print(sd.list(folder))

    def test_requests_session(self):
        """tests the ags connection through the idea"""
        url = "https://rextapilnxsvr01.esri.com/server/rest/services/System"
        with EsriSession(
            auth=ArcGISServerAuth(ags_file=r"./myserver.ags"),
            proxies=PROXIES,
            verify_cert=False,
        ) as session:
            resp = session.get(url=url, params={"f": "json"})
            data = resp.json()
            assert data
            assert len(data["services"]) > 0


if __name__ == "__main__":
    unittest.main()
