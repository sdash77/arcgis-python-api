import sys
import os, shutil, tempfile
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


profiles = ["your_online_admin_profile", "your_ent_admin_profile"]
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestInfoFileOps(unittest.TestCase):
    def test_package_info(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            items = gis.content.search("Map Package")
            if len(items) > 0:
                fp = items[0].package_info()
                assert fp
                os.remove(fp)
                fp = items[0].package_info(tempfile.gettempdir())
                assert fp
                os.remove(fp)

    def test_item_card(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            items = gis.content.search("Map Package")
            if len(items) > 0:
                fp = items[0].item_card
                assert fp
                os.remove(fp)

    def test_update_info(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            items = gis.content.search("Map Package")
            if len(items) > 0:
                fp = items[0].item_card
                assert fp

                updated = items[8].update_info(fp)
                assert updated
                assert updated["success"] is True
                os.remove(fp)


if __name__ == "__main__":
    unittest.main()
