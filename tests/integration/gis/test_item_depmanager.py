import sys
import unittest

from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.gis.sharing._dependency import DependencyManager
from utils.decorators import integration_test

PROFILES = ["your_ent_admin_profile"]
ALL_HTTP = True


@integration_test
class TestDependencyManager(unittest.TestCase):
    def test_agol_is_none(self):
        profile = "your_online_profile"
        gis = GIS(profile=profile, verify_cert=False, proxy=detect_proxy(ALL_HTTP))
        dm = gis.content.dependency_manager
        assert dm is None

    def test_rebuild(self):
        for profile in PROFILES:
            print(profile)
            gis = GIS(profile=profile, verify_cert=False, proxy=detect_proxy(ALL_HTTP))
            assert isinstance(gis.content.dependency_manager, DependencyManager)
            dm = gis.content.dependency_manager
            assert dm.rebuild()

    def test_stop(self):
        for profile in PROFILES:
            print(profile)
            gis = GIS(profile=profile, verify_cert=False, proxy=detect_proxy(ALL_HTTP))

            dm = gis.content.dependency_manager
            assert dm.terminate()

    def test_status(self):
        for profile in PROFILES:
            print(profile)
            gis = GIS(profile=profile, verify_cert=False, proxy=detect_proxy(ALL_HTTP))

            dm = gis.content.dependency_manager
            assert dm.status


if __name__ == "__main__":
    unittest.main()
