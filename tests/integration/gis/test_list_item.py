import sys

#
#  Update the Path to set the test area
# sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
#
import os, shutil, tempfile
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS

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


class TestListItem(unittest.TestCase):
    def test_list_item(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            items = gis.content.search("*", item_type="Feature Layer")
            for item in items:
                if item.owner == gis.users.me.username:
                    try:
                        item.list
                        assert item["listed"] is True
                        print("listed: " + item["name"])
                    except:
                        continue
    
    def test_unlist_item(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            items = gis.content.search("*", item_type="Feature Layer")
            for item in items:
                if item.owner == gis.users.me.username:
                    try:
                        item.unlist
                        assert item["listed"] is False
                        print("unlisted: " + item["name"])
                    except:
                        continue

if __name__ == "__main__":
    unittest.main()