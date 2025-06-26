import os
import time
import unittest

from arcgis.gis._impl import ItemTypeEnum

from utils.decorators import profiles, integration_test
from integration.config import QALAB_ROOT_PATH, copy_as_tempfile
from utils.data_utils import add_source_item, cleanup_published_items


@profiles.enterprise_and_agol
@integration_test
class TestPublish3DFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.items = []
        uid = int(time.time())

        data_philly_path = os.path.join(
            QALAB_ROOT_PATH, "gis_mod_3dtiles_package", "Philly.3tz"
        )
        data_philly = copy_as_tempfile(data_philly_path)

        # data originally from \\qalab_server\checklist_data\SceneLayers\3DTiles\ESRICreated\with_compression
        data_philly_textured_path = os.path.join(
            QALAB_ROOT_PATH, "gis_mod_3dtiles_package", "PhillyTextured.3tz"
        )
        data_philly_textured = copy_as_tempfile(data_philly_textured_path)

        cls.philly_package = add_source_item(
            cls.gis,
            f"NewTilePackage3D_philly_{uid}",
            ItemTypeEnum.TILES_PACKAGE_3D,
            data_philly,
        )
        assert cls.philly_package, "3D tiles item not added"
        cls.items.append(cls.philly_package)
        cls.philly_textured_package = add_source_item(
            cls.gis,
            f"NewTilePackage3D_phillyTextured_{uid}",
            ItemTypeEnum.TILES_PACKAGE_3D,
            data_philly_textured,
        )
        assert cls.philly_textured_package, "3D textured item not added"
        cls.items.append(cls.philly_textured_package)

    def test_publish_3dtile_3dobject(self):
        new_item = self.philly_textured_package.publish()
        self.assertIsNotNone(new_item)
        self.items.append(new_item)
        self.assertEqual(new_item.type, "3DTiles Service")

    def test_publish_3dtile_integrated_mesh(self):
        new_item = self.philly_package.publish()
        self.assertIsNotNone(new_item)
        self.items.append(new_item)
        self.assertEqual(new_item.type, "3DTiles Service")

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items(cls.items)


if __name__ == "__main__":
    unittest.main()
