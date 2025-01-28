import os
import time
import unittest
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test, profiles
from arcgis.gis import Item
from arcgis.features.managers import FeatureLayerCollectionManager
from utils.data_utils import ItemType, publish_test_item, cleanup_published_items


@profiles.enterprise_and_agol
@integration_test
class TestFeatureLayerCollectionManager(unittest.TestCase):
    """
    Test to check if a FeatureLayerCollectionManager object works
    """

    # Add fields to allow for the cleanup method to work
    data_item = None
    wfl_item = None
    is_agol = False

    @classmethod
    def setUpClass(cls):
        """
        Get class test asset location
        :return:
        """
        cls.uid = int(time.time())

        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_cls_path = os.path.join(
            cls.qalab_base_path, "features_mod_FeatureLayerCollectionManager_cls_short"
        )

        is_agol = cls.profile == "your_online_profile"
        # Hold all Items for cleanup
        cls.items = []

    def test_create_FeatureLayerCollectionManager_object(self):
        """
        Test creating instances of FeatureLayerCollectionManager class in multiple ways
        :return:
        """

        try:
            # region Publish the feature layer if it does not exist
            layer_name = f"dino_FLC_basic_{self.uid}"
            data_path = os.path.join(self.qalab_cls_path, "simple_points.csv")
            published_item = publish_test_item(
                gis=self.gis,
                layer_name=layer_name,
                source_data_path=data_path,
                item_type=ItemType.CSV.value,
                prep_for_editing=False,
            )
            self.assertIsInstance(published_item, Item)
            self.items.append(published_item)

            # check a FeatureLayerCollectionManager object can be created from url
            flcm_url = FeatureLayerCollectionManager(published_item.url, self.gis)
            self.assertIsInstance(
                flcm_url,
                FeatureLayerCollectionManager,
                "Cannot create a FeatureLayerCollectionManager obj from url",
            )

            # check FeatureLayerCollectionManager object can be created from item
            flcm_item = FeatureLayerCollectionManager.fromitem(published_item)
            self.assertIsInstance(
                flcm_item,
                FeatureLayerCollectionManager,
                "Cannot create a FeatureLayerCollectionManager from item",
            )

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    def test_overwrite_HFS_using_csv(self):
        """
        Publish a feature layer with csv.
        Update the csv and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """

        try:
            data_path = os.path.join(self.qalab_cls_path, "overwrite_HFS_csv.csv")
            layer_name = f"overwrite_HFS_csv_{self.uid}"
            published_item = publish_test_item(
                gis=self.gis,
                layer_name=layer_name,
                source_data_path=data_path,
                item_type=ItemType.CSV.value,
                prep_for_editing=False,
            )
            self.assertIsInstance(published_item, Item)
            self.items.append(published_item)

            # delete all features in feature layer
            flayer = published_item.layers[0]
            delete_result = flayer.delete_features(where="1=1")
            self.assertIsNotNone(
                delete_result, "Unable to delete features before overwrite"
            )
            num_features_after_delete = flayer.query(return_count_only=True)
            self.assertEqual(
                num_features_after_delete, 0, "Num features not 0 after delete all"
            )

            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(published_item)

            # overwrite the feature layer
            new_data_path = os.path.join(
                self.qalab_cls_path, "overwrite_wfl", "overwrite_HFS_csv.csv"
            )
            overwrite_result = flc_mgr.overwrite(new_data_path)
            self.assertIsNotNone(
                overwrite_result, "Calling publish with overwrite True returns None"
            )

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(
                num_features_after_overwrite, 0, "Overwrite failed to add new features"
            )

            # verify csv shape
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf
            self.assertEqual(
                (20, 8),
                overwritten_flayer_df.shape,
                "The number of rows cols of overwritten feature layer is not more than original",
            )

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    def test_overwrite_HFS_using_excel(self):
        """
        Publish a feature layer with excel.
        Update the excel and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        *Note: does not work if hosted table
        :return:
        """

        try:
            data_path = os.path.join(self.qalab_cls_path, "overwrite_HFS_excel.xlsx")
            layer_name = f"overwrite_HFS_excel_{self.uid}"
            published_item = publish_test_item(
                gis=self.gis,
                layer_name=layer_name,
                source_data_path=data_path,
                item_type=ItemType.EXCEL.value,
                prep_for_editing=False,
            )
            self.assertIsInstance(published_item, Item)
            self.items.append(published_item)

            # region delete all features in feature layer
            flayer = published_item.layers[0]
            delete_result = flayer.delete_features(where="1=1")
            self.assertIsNotNone(
                delete_result, "Unable to delete features before overwrite"
            )
            num_features_after_delete = flayer.query(return_count_only=True)
            self.assertEqual(
                num_features_after_delete, 0, "Num features not 0 after delete all"
            )

            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(published_item)

            # overwrite the feature layer
            new_data_path = os.path.join(
                self.qalab_cls_path, "overwrite_wfl", "overwrite_HFS_excel.xlsx"
            )
            overwrite_result = flc_mgr.overwrite(new_data_path)
            self.assertIsNotNone(
                overwrite_result, "Calling publish with overwrite True returns None"
            )

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(
                num_features_after_overwrite, 0, "Overwrite failed to add new features"
            )

            # verify excel shape
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf
            self.assertEqual(
                (20, 8),
                overwritten_flayer_df.shape,
                "The number of rows cols of overwritten feature layer is not more than original",
            )

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    def test_overwrite_HFS_using_fgdb(self):
        """
        Publish a feature layer with file geodatabase.
        Update the fgdb and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """

        try:
            # region publish feature layer
            data_path = os.path.join(self.qalab_cls_path, "overwrite_HFS_fgdb.gdb.zip")
            layer_name = f"overwrite_HFS_fgdb_{self.uid}"
            published_item = publish_test_item(
                gis=self.gis,
                layer_name=layer_name,
                source_data_path=data_path,
                item_type=ItemType.FGDB.value,
                prep_for_editing=False,
            )
            self.assertIsInstance(published_item, Item)
            self.items.append(published_item)
            # endregion

            # region delete all features in feature layer
            flayer = published_item.layers[0]
            delete_result = flayer.delete_features(where="1=1")
            self.assertIsNotNone(
                delete_result, "Unable to delete features before overwrite"
            )
            num_features_after_delete = flayer.query(return_count_only=True)
            self.assertEqual(
                num_features_after_delete, 0, "Num features not 0 after delete all"
            )
            # endregion

            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(published_item)

            # overwrite the feature layer
            new_fgdb_path = os.path.join(
                self.qalab_cls_path, "overwrite_wfl", "overwrite_HFS_fgdb.gdb.zip"
            )
            overwrite_result = flc_mgr.overwrite(new_fgdb_path)
            self.assertIsNotNone(
                overwrite_result, "Calling publish with overwrite True returns None"
            )

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(
                num_features_after_overwrite, 0, "Overwrite failed to add new features"
            )

            # verify fgdb shape
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf
            self.assertEqual(
                (20, 8),
                overwritten_flayer_df.shape,
                "The number of rows cols of overwritten feature layer is not more than original",
            )
        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    def test_overwrite_HFS_using_shp(self):
        """
        Publish a feature layer with shape file
        Update the shp and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """

        try:
            data_path = os.path.join(self.qalab_cls_path, "overwrite_HFS_shp.zip")
            layer_name = f"overwrite_HFS_shp_{self.uid}"
            published_item = publish_test_item(
                gis=self.gis,
                layer_name=layer_name,
                source_data_path=data_path,
                item_type=ItemType.SHP.value,
                prep_for_editing=False,
            )
            self.assertIsInstance(published_item, Item)
            self.items.append(published_item)
            # endregion

            # region delete all features in feature layer
            flayer = published_item.layers[0]
            delete_result = flayer.delete_features(where="1=1")
            self.assertIsNotNone(
                delete_result, "Unable to delete features before overwrite"
            )
            num_features_after_delete = flayer.query(return_count_only=True)
            self.assertEqual(
                num_features_after_delete, 0, "Num features not 0 after delete all"
            )
            # endregion

            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(published_item)

            # overwrite the feature layer
            new_data_path = os.path.join(
                self.qalab_cls_path, "overwrite_wfl", "overwrite_HFS_shp.zip"
            )
            overwrite_result = flc_mgr.overwrite(new_data_path)
            self.assertIsNotNone(
                overwrite_result, "Calling publish with overwrite True returns None"
            )

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(
                num_features_after_overwrite, 0, "Overwrite failed to add new features"
            )

            # verify shp shape
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf
            self.assertEqual(
                (20, 8),
                overwritten_flayer_df.shape,
                "The number of rows cols of overwritten feature layer is not more than original",
            )

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(is_agol, "Will fail on agol with service name duplicate")
    def test_overwrite_HFS_using_sd(self):
        """
        Publish a feature layer with SD file
        Update the sd with another SD that is not marked for overwriting and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """

        try:
            data_path = os.path.join(self.qalab_cls_path, "overwrite_HFS_sd.sd")
            layer_name = f"overwrite_HFS_sd_{self.uid}"
            published_item = publish_test_item(
                gis=self.gis,
                layer_name=layer_name,
                source_data_path=data_path,
                item_type=ItemType.SD.value,
                prep_for_editing=False,
            )
            self.assertIsInstance(published_item, Item)
            self.items.append(published_item)
            # endregion

            # region delete all features in feature layer
            flayer = published_item.layers[0]
            delete_result = flayer.delete_features(where="1=1")
            self.assertIsNotNone(
                delete_result, "Unable to delete features before over write"
            )
            num_features_after_delete = flayer.query(return_count_only=True)
            self.assertEqual(
                num_features_after_delete, 0, "Num features not 0 after delete all"
            )
            # endregion

            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(published_item)

            # overwrite the feature layer
            new_data_path = os.path.join(
                self.qalab_cls_path, "overwrite_wfl", "overwrite_HFS_sd.sd"
            )
            overwrite_result = flc_mgr.overwrite(new_data_path)
            self.assertIsNotNone(
                overwrite_result, "Calling publish with overwrite True returns None"
            )

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(
                num_features_after_overwrite, 0, "Overwrite failed to add new features"
            )

            # verify sd shape
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf
            self.assertEqual(
                (20, 8),
                overwritten_flayer_df.shape,
                "The number of rows cols of overwritten feature layer is not more than original",
            )

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items(cls.items)


if __name__ == "__main__":
    unittest.main()
