import os
import unittest
from utils.decorators import profiles, integration_test
from config import QALAB_ROOT_PATH


@profiles.enterprise_and_agol
@integration_test
class TestPublish3DFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.folder = cls.gis.content.folders._get_or_create(
            folder="integration_testing_gis_content_3dtile_pkg_publish",
            owner=cls.gis._username
        )

        # data originally from \\qalab_server\checklist_data\SceneLayers\3DTiles\ESRICreated\with_compression
        data_philly_textured = os.path.join(QALAB_ROOT_PATH, "gis_mod_3dtiles_package", "PhillyTextured.3tz")
        data_philly = os.path.join(QALAB_ROOT_PATH, "gis_mod_3dtiles_package", "Philly.3tz")

        # add data to portal
        cls.philly_package = cls.folder.add(
            {
                "title": "NewTilePackage3D_philly",
                "tags": "integration_testing",
                "type": "3DTiles Package"
            },
            file=data_philly,
        ).result()
        cls.philly_textured_package = cls.folder.add(
            {
                "title": "NewTilePackage3D_phillyTextured",
                "tags": "integration_testing",
                "type": "3DTiles Package"
            },
            file=data_philly_textured,
        ).result()

    def test_publish_3dtile_3dobject(self):

        if not self.gis._is_agol:
            if self.gis.version < [2024, 2]:
                self.skipTest("Publishing hosted tile layer functionality is available in enterprise is 11.4+")

        new_item = self.philly_textured_package.publish()
        self.assertIsNotNone(new_item)
        self.assertEqual(new_item.type, "3DTiles Service")
        self.assertTrue(new_item.delete(permanent=True))

    def test_publish_3dtile_integrated_mesh(self):

        if not self.gis._is_agol:
            if self.gis.version < [2024, 2]:
                self.skipTest("Publishing hosted tile layer functionality is available in enterprise is 11.4+")

        new_item = self.philly_package.publish()
        self.assertIsNotNone(new_item)
        self.assertEqual(new_item.type, "3DTiles Service")
        self.assertTrue(new_item.delete(permanent=True))

    @classmethod
    def tearDownClass(cls):
        if cls.philly_textured_package:
            assert cls.philly_textured_package.delete(permanent=True)
        if cls.philly_package:
            assert cls.philly_package.delete(permanent=True)
        if cls.folder:
            assert cls.folder.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
