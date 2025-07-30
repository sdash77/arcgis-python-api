import os
import time
import unittest
from arcgis.features.managers import AttachmentManager
from arcgis.gis import Item
from arcgis.gis._impl import ItemTypeEnum
from utils.data_utils import publish_test_item, cleanup_published_items
from utils.decorators import integration_test, profiles
from integration.config import get_resource_path


@profiles.enterprise_and_agol
@integration_test
class TestAttachmentManager(unittest.TestCase):
    """
    Test for AttachmentManager object
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up data path and test_item
        """
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
            layer_name=f"ntgrtn_tst_AttachmentManager_{uid}",
            source_data_path=sd_file_path,
            item_type=ItemTypeEnum.FILE_GEODATABASE,
        )
        assert isinstance(cls.test_item, Item), "Published item is not an Item"

    def test_create_AttachmentManager_object(self):
        """
        Test create instances of AttachmentManager class in multiple ways
        :return:
        """
        # create FeatureLayerManager object from item feature layer
        fl = self.test_item.layers[0]
        fl_amgr = fl.attachments
        assert isinstance(fl_amgr, AttachmentManager)

        # create FeatureLayerManager object from item
        fl_amgr2 = AttachmentManager(self.test_item)
        assert isinstance(fl_amgr2, AttachmentManager)

    def test_getlist_and_download_attachment(self):
        """
        Test download attachment using AttachmentManager
        """
        fl = self.test_item.layers[0]
        fl_am = fl.attachments
        attachment_list = fl_am.get_list(2)
        self.assertTrue(
            len(attachment_list) >= 1, "At least 1 attchment should be found"
        )
        attachment_id = attachment_list[0]["id"]
        self.assertEqual(2, attachment_id, f"attachment id mismatch: {attachment_id}")
        self.assertEqual(
            "cows2.jpg", attachment_list[0]["name"], "attachment name mismatch"
        )

        # download png
        png_list = fl_am.get_list(2)
        png_id = png_list[0]["id"]
        download_result_png = fl.attachments.download(2, png_id)
        self.assertIsInstance(
            download_result_png[0], str, "Download result is not a string."
        )

        # download pdf
        pdf_list = fl_am.get_list(2)
        pdf_item = [i for i in pdf_list if i.get("name", "att_name") == "crime_pdf.pdf"]
        pdf_id = pdf_item[0]["id"]
        download_result_pdf = fl.attachments.download(2, pdf_id)
        download_pdf_path = download_result_pdf[0]
        self.assertTrue(
            ".pdf" in download_pdf_path,
            f"Incorrect attachment file extension: {download_pdf_path}",
        )

        # download all
        download_result_all = fl.attachments.download()
        self.assertEqual(
            3,
            len(download_result_all),
            f"Incorrect attachment count via all. Got {len(download_result_all)}",
        )

        # download a list of feature oid
        download_result_listoid = fl.attachments.download([1, 2])
        download_count = len(download_result_listoid)
        self.assertEqual(
            3,
            download_count,
            f"Incorrect attachment count via OID list. Got {download_count}",
        )

        # download multiple attachment from one feature
        download_result_multi = fl.attachments.download(2)
        download_one_feature = len(download_result_multi)
        self.assertEqual(
            2,
            download_one_feature,
            f"Incorrect attachment count via one feature. Got {download_one_feature}",
        )

    def test_add_update_delete_attachment(self):
        """
        Test count attachment
        """
        fl = self.test_item.layers[0]
        fl_am = fl.attachments
        initial_attachment_count = fl_am.count()
        self.assertEqual(
            3,
            initial_attachment_count,
            f"Incorrect initial attachment count: {initial_attachment_count}",
        )

        # add
        add_res = fl_am.add(1, self.new_attachment)
        self.assertTrue(
            add_res["addAttachmentResult"]["success"], "Add attachment failed"
        )
        added_attachment_count = fl_am.count()
        self.assertEqual(
            4,
            added_attachment_count,
            f"Incorrect attachment count after add: {added_attachment_count}",
        )

        # update
        attachment_id = fl_am.get_list(1)[0]["id"]
        update_res = fl_am.update(1, attachment_id, self.update_attachment)

        self.assertTrue(
            update_res.get("updateAttachmentResult").get("success"),
            "Update attachment failed",
        )
        self.assertIsNotNone(
            update_res.get("updateAttachmentResult"),
            "Updated attachment result is None.",
        )

        # delete
        delete_res = fl_am.delete(1, attachment_id)
        self.assertTrue(
            delete_res["deleteAttachmentResults"][0]["success"],
            "Delete attachment failed",
        )
        deleted_attachment_count = fl_am.count()
        self.assertEqual(
            3,
            deleted_attachment_count,
            f"Incorrect attachment count after add: {deleted_attachment_count}",
        )

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items([cls.test_item])


if __name__ == "__main__":
    unittest.main()
