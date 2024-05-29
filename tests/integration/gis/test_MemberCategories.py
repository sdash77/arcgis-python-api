import sys

import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, ProfileManager
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)


profiles = [
    'your_online_admin_profile',
]


PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestMemberCategories(unittest.TestCase):
    """
    Tests the new member categories endpoints.
    """

    def test_categories(self):
        """Asserts that the property is not null"""
        for profile in profiles:
            gis = GIS(profile=profile, proxy=PROXIES, verify_cert=False)
            assert gis.users.categories  # gets the Cateogires

    def test_assignment(self):
        """tests the assignment of the categories"""
        for profile in profiles:
            gis = GIS(profile=profile, proxy=PROXIES, verify_cert=False)
            categories = [
                {
                    "title": "amazing",
                    "categories": [
                        {
                            "title": "test",
                            "categories": [{"title": "test lower"}],
                        },
                        {"title": "Sub2"},
                    ],
                },
                {"title": "Top Category 2"},
            ]
            gis.users.categories = categories
            assert gis.users.categories[0]['categories']

    def test_delete_categories(self):
        """Asserts that the property is not null"""
        for profile in profiles:
            gis = GIS(profile=profile, proxy=PROXIES, verify_cert=False)
            gis.users.categories = None
            assert gis.users.categories is None

    def test_user_assignment(self):
        """tests the user assignment of a category"""
        for profile in profiles:
            gis = GIS(profile=profile, proxy=PROXIES, verify_cert=False)
            categories = [
                {
                    "title": "amazing",
                    "categories": [
                        {
                            "title": "test",
                            "categories": [{"title": "test lower"}],
                        },
                        {"title": "Sub2"},
                    ],
                },
                {"title": "Top Category 2"},
            ]
            gis.users.categories = categories
            assert gis.users.assign_categories(
                [gis.users.me],
                ["/Categories/amazing/test/test lower", "amazing"],
            )
            assert gis.users.me.categories == [
                "/Categories/amazing/test/test lower",
                "/Categories/amazing",
            ]


if __name__ == "__main__":
    unittest.main()
