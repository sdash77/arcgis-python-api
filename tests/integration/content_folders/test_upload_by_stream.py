import sys
import os
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, ContentManager, ItemProperties, ItemTypeEnum
from utils.decorators import integration_test, profiles
from integration.config import QALAB_ROOT_PATH

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
@profiles.enterprise_and_agol
class TestFolderStreamingAdd(unittest.TestCase):
    """
    Tests the streaming add
    """

    @classmethod
    def setUpClass(cls):
        cls.QA_LABS_FOLDER = os.path.join(QALAB_ROOT_PATH, "folder_add_content")
        cls.dataset = "servicedefinition.sd"

    def test_streaming_upload(self):
        gis = self.gis
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
