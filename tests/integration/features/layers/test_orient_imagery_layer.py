import unittest, os, uuid
from arcgis.features.layer import OrientedImageryLayer
from arcgis.gis._impl._dataclasses._contentds import (
    ItemTypeEnum,
    ItemProperties,
)
from utils.decorators import integration_test, profiles
from integration.config import QALAB_ROOT_PATH
from utils.data_utils import cleanup_published_items
from utils._logging import enable_verbose_logging

enable_verbose_logging()

QA_LABS = QALAB_ROOT_PATH + r"\oriented_image_layer"
DATASET = "OI_sample.gdb.zip"


@profiles.enterprise_and_agol
@integration_test
class TestOrientedImageryLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        PDATA = os.path.join(QA_LABS, DATASET)
        name = f"FGDB_{uuid.uuid4().hex[: 4]}"
        ip = ItemProperties(
            **{
                "item_type": ItemTypeEnum.FILE_GEODATABASE,
                "title": name,
                "tags": "ntgrtn-tst",
            }
        )
        cls.items = []
        cls.pitems = []

        item = cls.gis.content.add(item_properties=ip, data=PDATA)
        cls.published_item = item.publish({"name": name, "tags": "ntgrtn-tst"})

    def test_fromitem(self):
        """tests the from"""
        lyr = OrientedImageryLayer.fromitem(self.published_item)
        assert isinstance(lyr, OrientedImageryLayer)

    def test_create_OIL(self):
        """create OI Layer"""
        lyr = OrientedImageryLayer(
            url=f"{self.published_item.url}/0", gis=self.published_item._gis
        )
        assert isinstance(lyr, OrientedImageryLayer)

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items([cls.published_item])


if __name__ == "__main__":
    unittest.main()
