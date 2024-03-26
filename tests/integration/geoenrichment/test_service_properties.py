import sys
import logging
import unittest
import arcgis
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.geoenrichment._helper import service_properties
from utils.decorators import integration_test

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


@integration_test
class TestGEServiceProperties(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._gis_objs = []
        for profile in profiles:
            cls._gis_objs.append(
                GIS(profile=profile, proxy=PROXIES, verify_cert=False)
            )
            del profile

    def test_service_properties_case1(self):
        """Tests the method obtaining the GIS from the env and url"""
        case1 = service_properties()
        assert case1
        assert not "error" in case1
        assert "supportedOperations" in case1

    def test_service_properties_case2(self):
        """pass the GIS object only"""
        agol = service_properties(gis=self._gis_objs[0])
        assert agol
        assert not "error" in agol
        assert "supportedOperations" in agol
        ent = service_properties(gis=self._gis_objs[1])
        assert ent
        assert not "error" in ent
        assert "supportedOperations" in ent

    def test_service_properties_case3(self):
        gis: GIS = arcgis.env.active_gis
        url: str = f"{gis.properties['helperServices']['geoenrichment']['url']}/Geoenrichment"

        case3 = service_properties(url=url)
        assert case3
        assert not "error" in case3
        assert "supportedOperations" in case3

    def test_service_properties_case4(self):
        """pass the GIS and URL"""
        for gis in self._gis_objs:
            url: str = f"{gis.properties['helperServices']['geoenrichment']['url']}/Geoenrichment"
            case4 = service_properties(url=url, gis=gis)
            assert case4
            assert not "error" in case4
            assert "supportedOperations" in case4


if __name__ == "__main__":
    unittest.main()
