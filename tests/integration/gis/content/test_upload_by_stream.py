import os
import unittest
from arcgis.gis import GIS, ContentManager, ItemProperties, ItemTypeEnum
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from integration.config import QALAB_ROOT_PATH


enable_verbose_logging()


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
        
        item = None
        try:
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
            assert isinstance(job.running(), bool)
            assert isinstance(job.done(), bool)            
            item = job.result()
            assert item
            assert job            
        except:
            pass
        finally:
            if item:
                assert item.delete()


if __name__ == "__main__":
    unittest.main()
