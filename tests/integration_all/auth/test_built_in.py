import sys

try:
    from _utils import get_config_parser
except:
    from ._utils import get_config_parser
import unittest
from arcgis.gis import GIS
from arcgis.auth import EsriGenTokenAuth

PROFILES = ["your_online_profile", "your_enterprise_profile"]

from utils.decorators import integration_test


@integration_test
class TestBuiltIn(unittest.TestCase):
    """tests the username/password with ago and enterprise"""

    def test_built_in_eneterprise(self):
        """tests the enterprise login"""
        gis = GIS(profile=PROFILES[1])
        assert gis.users.me

    def test_built_in_agol(self):
        """tests the AGO login"""
        gis = GIS(profile=PROFILES[0])
        assert gis.users.me

    def test_built_in_handler(self):
        gis = GIS(profile=PROFILES[0], use_gen_token=True)
        assert isinstance(gis._con._session.auth, EsriGenTokenAuth)
        assert gis.users.me


if __name__ == "__main__":
    unittest.main()
