import os
import time
import unittest
from utils.decorators import integration_test, profiles
from arcgis.gis import Item, GIS
from arcgis.features.managers import FeatureLayerCollectionManager
from utils.data_utils import publish_test_item, cleanup_published_items
from arcgis.gis._impl._dataclasses._contentds import ItemTypeEnum
from integration.config import get_resource_path


@profiles.all
@integration_test
class TestFeatureLayerCollectionManager(unittest.TestCase):
    """
    Test to check if a FeatureLayerCollectionManager object works
    """

    # Add fields to allow for the cleanup method to work
    data_item = None
    wfl_item = None
    is_agol = True

    @classmethod
    def setUpClass(cls):
        """
        Get class test asset location
        :return:
        """
        cls.uid = int(time.time())
        # Hold all Items for cleanup
        cls.published_items = []

    def test_create_FeatureLayerCollectionManager_object(self):
        """
        Test creating instances of FeatureLayerCollectionManager class in multiple ways
        :return:
        """
        # region Publish the feature layer if it does not exist
        layer_name = f"test_flc_object_{self.uid}"
        data_path = get_resource_path(
            "staging_data/feature_object/simple_points.csv", unique_copy=True
        )

        published_item = publish_test_item(
            gis=self.gis,
            layer_name=layer_name,
            source_data_path=data_path,
            item_type=ItemTypeEnum.CSV,
            prep_for_editing=False,
        )
        self.assertIsInstance(published_item, Item, "Incorrect item type")
        self.published_items.append(published_item)

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

    def test_overwrite_HFS_using_csv(self):
        """
        Publish a feature layer with csv.
        Update the csv and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        layer_name = f"overwrite_HFS_csv_{self.uid}"
        data_path = get_resource_path(
            "staging_data/feature_object/overwrite_HFS_csv.csv", unique_copy=True
        )

        published_item = publish_test_item(
            gis=self.gis,
            layer_name=layer_name,
            source_data_path=data_path,
            item_type=ItemTypeEnum.CSV,
            prep_for_editing=False,
        )
        self.assertIsInstance(published_item, Item, "Incorrect item type")
        self.published_items.append(published_item)

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
        temp_new_data_path = get_resource_path(
            "staging_data/feature_object/overwrite/overwrite_HFS_csv.csv",
            unique_copy=True,
        )
        new_data_path = self.rename_overwrite_filename(data_path, temp_new_data_path)
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

    def test_overwrite_HFS_using_excel(self):
        """
        Publish a feature layer with excel.
        Update the excel and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        *Note: does not work if hosted table
        :return:
        """
        layer_name = f"overwrite_HFS_excel_{self.uid}"
        data_path = get_resource_path(
            "staging_data/feature_object/overwrite_HFS_excel.xlsx", unique_copy=True
        )
        published_item = publish_test_item(
            gis=self.gis,
            layer_name=layer_name,
            source_data_path=data_path,
            item_type=ItemTypeEnum.MICROSOFT_EXCEL,
            prep_for_editing=False,
        )
        self.assertIsInstance(published_item, Item, "Incorrect item type")
        self.published_items.append(published_item)

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
        temp_new_data_path = get_resource_path(
            "staging_data/feature_object/overwrite/overwrite_HFS_excel.xlsx",
            unique_copy=True,
        )
        new_data_path = self.rename_overwrite_filename(data_path, temp_new_data_path)
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

    def test_overwrite_HFS_using_fgdb(self):
        """
        Publish a feature layer with file geodatabase.
        Update the fgdb and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region publish feature layer
        layer_name = f"overwrite_HFS_fgdb_{self.uid}"
        data_path = get_resource_path(
            "staging_data/feature_object/overwrite_HFS_fgdb.gdb.zip", unique_copy=True
        )
        published_item = publish_test_item(
            gis=self.gis,
            layer_name=layer_name,
            source_data_path=data_path,
            item_type=ItemTypeEnum.FILE_GEODATABASE,
            prep_for_editing=False,
        )
        self.assertIsInstance(published_item, Item, "Incorrect item type")
        self.published_items.append(published_item)
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
        temp_new_data_path = get_resource_path(
            "staging_data/feature_object/overwrite/overwrite_HFS_fgdb.gdb.zip",
            unique_copy=True,
        )
        new_data_path = self.rename_overwrite_filename(data_path, temp_new_data_path)
        overwrite_result = flc_mgr.overwrite(new_data_path)
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

    def test_overwrite_HFS_using_shp(self):
        """
        Publish a feature layer with shape file
        Update the shp and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        layer_name = f"overwrite_HFS_shp_{self.uid}"
        data_path = get_resource_path(
            "staging_data/feature_object/overwrite_HFS_shp.zip", unique_copy=True
        )
        published_item = publish_test_item(
            gis=self.gis,
            layer_name=layer_name,
            source_data_path=data_path,
            item_type=ItemTypeEnum.SHAPEFILE,
            prep_for_editing=False,
        )
        self.assertIsInstance(published_item, Item, "Incorrect item type")
        self.published_items.append(published_item)
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
        temp_new_data_path = get_resource_path(
            "staging_data/feature_object/overwrite/overwrite_HFS_shp.zip",
            unique_copy=True,
        )
        new_data_path = self.rename_overwrite_filename(data_path, temp_new_data_path)
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

    def test_overwrite_HFS_using_sd(self):
        """
        Publish a feature layer with SD file
        Update the sd with another SD that is not marked for overwriting and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        sd_file_name = "overwrite_HFS_sd.sd"
        if self.gis._is_agol:
            sd_file_name = "overwrite_HFS_sd_agol.sd"
        data_path = get_resource_path(
            f"staging_data/feature_object/{sd_file_name}", unique_copy=True
        )
        layer_name = f"overwrite_HFS_sd_{self.uid}"
        published_item = publish_test_item(
            gis=self.gis,
            layer_name=layer_name,
            source_data_path=data_path,
            item_type=ItemTypeEnum.SERVICE_DEFINITION,
            prep_for_editing=False,
        )
        self.assertIsInstance(published_item, Item, "Incorrect item type")
        self.published_items.append(published_item)
        # endregion

        # region delete all features in feature layer
        flayer = published_item.layers[0]
        fset = flayer.query()
        flayer_df = fset.sdf

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
        temp_new_data_path = get_resource_path(
            f"staging_data/feature_object/overwrite/{sd_file_name}",
            unique_copy=True,
        )
        new_data_path = self.rename_overwrite_filename(data_path, temp_new_data_path)
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

    @classmethod
    def rename_overwrite_filename(cls, original_path, overwrite_file_path):
        original_filename = os.path.basename(original_path)
        overwrite_dirname = os.path.dirname(overwrite_file_path)
        new_overwrite_file_path = os.path.join(overwrite_dirname, original_filename)
        try:
            os.rename(overwrite_file_path, new_overwrite_file_path)
            if not os.path.exists(new_overwrite_file_path):
                raise FileNotFoundError(
                    f"Could not find file: {new_overwrite_file_path}"
                )
            return new_overwrite_file_path
        except Exception as ex:
            print(ex)
            return None

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items(cls.published_items)


if __name__ == "__main__":
    unittest.main()
