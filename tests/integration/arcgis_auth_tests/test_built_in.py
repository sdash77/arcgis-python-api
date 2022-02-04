import sys

# sys.path.insert(0, r"c:\SVN\geosaurus_master_issue_4790a\src")
import unittest
from arcgis.gis import GIS

PROFILES = ["your_online_profile", "your_enterprise_profile"]


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


if __name__ == "__main__":
    unittest.main()
