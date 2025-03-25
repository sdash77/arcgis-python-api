import sys
sys.path.insert(0, r"C:\workspace\geosaurus\tests")
import unittest
from utils.decorators import integration_test, profiles
from arcgis.map import Map
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

        m = Map()
        m.content.add(self.test_item)
        m.save({"title": "test_attachments_size", "tags": "test", "snippet": "test"})
        
        assert len(m.content.layers) == 1
        map_item = m.item
        assert map_item
        assert map_item.attachments_size
        
        assert m.delete()
        

if __name__ == "__main__":
    unittest.main()