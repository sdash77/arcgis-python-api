import unittest
from utils.decorators import integration_test, profiles


@profiles.enterprise_and_agol
@integration_test
class TestAttachmentManagerCount(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.layer_info = {}
        search_result = cls.gis.content.search(
            "dino_AttachmentManager_basic", "Feature Layer"
        )
        if len(search_result) > 0:
            cls.layer_info[cls.gis.url] = search_result[0]
        else:
            cls.layer_info[cls.gis.url] = None

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
