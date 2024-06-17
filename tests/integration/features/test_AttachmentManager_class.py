import os
import unittest
from arcgis.features.managers import AttachmentManager
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test, profiles


@profiles.enterprise_and_agol
@integration_test
class TestAttachmentManager(unittest.TestCase):
    """
    Test for AttachmentManager object
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up QALAB path and test_item
        """
        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_cls_path = os.path.join(
            cls.qalab_base_path, "features_mod_AttachmentManager_cls"
        )
        cls.new_attachment = os.path.join(cls.qalab_cls_path, "cows3.jpg")
        cls.update_attachment = os.path.join(cls.qalab_cls_path, "cows4.jpg")

        cls.test_item = cls.gis.content.search(
            "dino_AttachmentManager_basic", "Feature Layer"
        )[0]

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
        attachment_list = fl_am.get_list(1)
        assert len(attachment_list) >= 1, "At least 1 attchment should be found"
        assert attachment_list[0]["id"] == 1, "attachment id mismatch"
        assert attachment_list[0]["name"] == "cows.jpg", "attachment name mismatch"

        # download png
        png_id = fl_am.get_list(1)[2]["id"]
        download_result_png = fl.attachments.download(1, png_id)
        assert isinstance(download_result_png[0], str)

        # download pdf
        pdf_id = fl_am.get_list(1)[1]["id"]
        download_result_pdf = fl.attachments.download(1, pdf_id)
        assert isinstance(download_result_pdf[0], str)

        # download all
        download_result_all = fl.attachments.download()
        assert isinstance(download_result_all, list)

        # download a list of feature oid
        download_result_listoid = fl.attachments.download([1, 2])
        assert isinstance(download_result_listoid, list)

        # download multiple attachment from one feature
        download_result_multi = fl.attachments.download(1)
        assert isinstance(download_result_multi, list)

    def test_add_update_delete_attachment(self):
        """
        Test count attachment
        """
        fl = self.test_item.layers[0]
        fl_am = fl.attachments

        # add
        add_res = fl_am.add(2, self.new_attachment)
        assert add_res["addAttachmentResult"]["success"]

        # update
        attachment_id = fl_am.get_list(2)[1]["id"]
        update_res = fl_am.update(2, attachment_id, self.update_attachment)
        assert update_res["updateAttachmentResult"]["success"]

        # delete
        delete_res = fl_am.delete(2, attachment_id)
        assert delete_res["deleteAttachmentResults"][0]["success"]

if __name__ == "__main__":
    unittest.main()
