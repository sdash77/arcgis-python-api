import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
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
class TestFavorites(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connections = [
            GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            for profile in profiles
        ]

    def test_get_favorites(self):
        """tests getting the favorites property"""
        for gis in self.connections:
            item = gis.content.search(f"owner: {gis.users.me.username}")[0]
            assert item.favorite in [True, False]

    def test_updating_favorites(self):
        """tests adding/removing an item to favorites"""
        for gis in self.connections:
            item = gis.content.search(f"owner: {gis.users.me.username}")[0]
            if item.favorite:
                item.favorite = False
                assert item.favorite == False
                item.favorite = True
            else:
                item.favorite = True
                item.shared_with
                assert item.favorite == True
                item.favorite = False


if __name__ == "__main__":
    unittest.main()
