import sys
sys.path.insert(0, r"C:\workspace\geosaurus\tests")
import unittest
from utils.decorators import integration_test, profiles

@profiles.agol
@integration_test
class TestAttachmentsSizeProperty(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Set up QALAB path and test_item
        """
        cls.test_item = cls.gis.content.search(
            "dino_AttachmentManager_basic", "Feature Layer"
        )[0]
        
    def test_attachments_size(self):
        """tests getting the count of attachments on a Feature Layer."""
        assert self.test_item
        assert self.test_item.subInfo
        assert self.test_item.attachments_size > 0


if __name__ == "__main__":
    unittest.main()