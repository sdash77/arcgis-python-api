import sys
import unittest

try:
    import arcpy

    SKIPTEST = False
except:
    SKIPTEST = True
from arcgis.gis import GIS


@unittest.skipIf(SKIPTEST, reason="missing arcpy")
class ProLoginTest(unittest.TestCase):
    """runs a simple pro login test"""

    def test_login_pro(self):
        arcpy.SignInToPortal(
            "https://www.arcgis.com/", "YesCreditsYesRoutingYesProNA", "redlands92373"
        )
        portal = GIS("PRO")
        assert portal.users.me


if __name__ == "__main__":
    unittest.main()
