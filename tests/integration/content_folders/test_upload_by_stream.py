import sys
import os
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, ContentManager, ItemProperties, ItemTypeEnum
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
class TestFolderStreamingAdd(unittest.TestCase):
    """
    Tests the streaming add
    """

    @classmethod
    def setUpClass(cls):
        cls.QA_LABS_FOLDER = (
            r"\\qalab_server\pydata\v109\geosaurus\folder_add_content"
        )
        cls.dataset = "servicedefinition.sd"

    def test_streaming_upload_enterprise(self):
        gis: GIS = GIS(profile=profiles[1], verify_cert=False, proxy=PROXIES)
        content: ContentManager = gis.content
        mgr = content.folders
        folder = mgr.get("Root Folder")
        ip = ItemProperties(
            title="test_streaming_upload",
            item_type=ItemTypeEnum.SERVICE_DEFINITION,
            overwrite=True,
        )
        job = folder.add(
            item_properties=ip,
            file=os.path.join(self.QA_LABS_FOLDER, self.dataset),
            item_id=None,
        )
        item = job.result()
        assert item
        assert job
        assert item.delete()

    def test_streaming_upload_online(self):
        gis: GIS = GIS(profile=profiles[0], verify_cert=False, proxy=PROXIES)
        content: ContentManager = gis.content
        mgr = content.folders
        folder = mgr.get("Root Folder")
        ip = ItemProperties(
            title="test_streaming_upload",
            item_type=ItemTypeEnum.SERVICE_DEFINITION,
            overwrite=True,
        )
        job = folder.add(
            item_properties=ip,
            file=os.path.join(self.QA_LABS_FOLDER, self.dataset),
            item_id=None,
        )
        item = job.result()
        assert item
        assert job
        assert item.delete()


if __name__ == "__main__":
    unittest.main()
