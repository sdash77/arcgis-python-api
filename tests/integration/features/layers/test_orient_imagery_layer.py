import unittest, os, uuid
from arcgis.features.layer import OrientedImageryLayer
from arcgis.gis._impl._dataclasses._contentds import (
    ItemTypeEnum,
    ItemProperties,
)
from utils.decorators import integration_test, profiles
from integration.config import QALAB_ROOT_PATH
from utils.data_utils import cleanup_published_items, publish_test_item
from utils._logging import enable_verbose_logging
from integration.config import get_resource_path

enable_verbose_logging()


@profiles.enterprise_and_agol
@integration_test
class TestOrientedImageryLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fgdb = get_resource_path("staging_data/oriented_imagery/OI_sample.gdb.zip")
        name = f"Oriented_Imagery_test_{uuid.uuid4().hex[: 4]}"

        cls.published_item = publish_test_item(
            cls.gis,
            name,
            fgdb,
            item_type=ItemTypeEnum.FILE_GEODATABASE,
            prep_for_editing=False,
        )

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
