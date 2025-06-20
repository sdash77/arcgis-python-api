import unittest
from arcgis.gis import GIS
from arcgis.gis.server.catalog import ServicesDirectory
from arcgis.gis._impl._profile import ServerProfileManager
from utils.decorators import integration_test

PROFILES = ["your_enterprise_profile"]


@integration_test
class TestServerProfileSD(unittest.TestCase):
    """Tests the server profile"""

    def test_service_directory(self):
        """
        Tests the Service Directory Connection
        """
        for profile in PROFILES:
            gis = GIS(profile=profile)
            sd = ServicesDirectory(
                url=gis._url.replace("/portal", "/server"),
                username=gis._username,
                password=gis._password,
                profile="server_profile",
                verify_cert=False,
            )
            del sd
            sd = ServicesDirectory(profile="server_profile", verify_cert=False)
            assert sd.properties
            assert sd.admin.logs.query()


if __name__ == "__main__":
    unittest.main()
