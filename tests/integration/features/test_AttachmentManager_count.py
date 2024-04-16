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
class TestAttachmentManagerCount(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._gis_objs = [
            GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            for profile in profiles
        ]
        cls.layer_info = {}
        for gis in cls._gis_objs:
            search_result = gis.content.search(
                "dino_AttachmentManager_basic", "Feature Layer"
            )
            if len(search_result) > 0:
                cls.layer_info[gis._url] = search_result[0]
            else:
                cls.layer_info[gis._url] = None

    def test_attachment_count(self):
        """tests getting the count of attachments on a Feature Layer."""
        for item in self.layer_info.values():
            if item:
                am = item.layers[0].attachments
                print(am.count(where="1=1"))

    def test_attachment_search(self):
        """ensures that the count == the search"""
        for item in self.layer_info.values():
            if item:
                am = item.layers[0].attachments
                count = am.count(where="1=1")
                assert count == len(am.search(where="1=1"))


if __name__ == "__main__":
    unittest.main()
