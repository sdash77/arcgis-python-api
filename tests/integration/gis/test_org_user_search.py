import sys
import logging

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter(' -  -  - ')
# handler.setFormatter(formatter)
root.addHandler(handler)

import unittest

import arcgis
from arcgis.gis import GIS
from utils.decorators import integration_test

print(arcgis.__file__)
print(arcgis.__version__)


@integration_test
class TestUserManagerOrgSearch(unittest.TestCase):
    """
    Tests the Org Search Method
    """

    def tests_org_search_anonymous(self):
        """when not logged in the response should always be zero users."""
        gis = GIS()
        with self.assertRaises(Exception):
            gis.users.org_search()

    def test_no_given_parameters(self):
        """tests method without parameters"""
        gis = GIS(profile="your_online_profile", verify_cert=False)
        assert gis.users.org_search()

    def test_star_given_parameters(self):
        """tests method with wildcards *"""
        gis = GIS(profile="your_online_profile", verify_cert=False)
        assert gis.users.org_search("*")

    def test_invalid_query_given_parameters(self):
        """tests method without parameters"""
        gis = GIS(profile="your_online_profile", verify_cert=False)
        assert len(gis.users.org_search("asdfasd43r3asdf")) == 0

    def test_valid_query_parameters(self):
        """tests method without parameters"""
        gis = GIS(profile="your_online_profile", verify_cert=False)
        assert gis.users.org_search("role: org_publisher")


if __name__ == "__main__":
    unittest.main()
