import time
import unittest

from arcgis.gis import Item
from arcgis.gis._impl import ItemTypeEnum
from utils.data_utils import publish_test_item, cleanup_published_items
from integration.config import get_resource_path
from utils.decorators import integration_test, profiles


@profiles.enterprise_and_agol
@integration_test
class TestAttachmentManagerCount(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.layer_info = {}
        uid = int(time.time())
        staging_data_path = "staging_data/attachments"
        sd_file_path = get_resource_path(
            f"{staging_data_path}/ntgrtn_tst_AttachmentManager.zip",
            unique_copy=True,
        )
        cls.new_attachment = get_resource_path(f"{staging_data_path}/cows3.jpg")
        cls.update_attachment = get_resource_path(f"{staging_data_path}/cows4.jpg")

        cls.test_item = publish_test_item(
            cls.gis,
            layer_name=f"ntgrtn_tst_AttachmentManager{uid}",
            source_data_path=sd_file_path,
            item_type=ItemTypeEnum.FILE_GEODATABASE,
        )
        assert isinstance(cls.test_item, Item), "Published item is not an Item"

    def test_attachment_count(self):
        """tests getting the count of attachments on a Feature Layer."""
        fl = self.test_item.layers[0]
        fl_am = fl.attachments
        attachment_count = fl_am.count(where="1=1")
        self.assertEqual(
            3, attachment_count, f"Incorrect attachment count: {attachment_count}"
        )

    def test_attachment_search(self):
        """ensures that the count == the search"""
        fl = self.test_item.layers[0]
        fl_am = fl.attachments
        count = fl_am.count(where="1=1")
        assert count == len(fl_am.search(where="1=1"))

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items([cls.test_item])


if __name__ == "__main__":
    unittest.main()
