# -----------------------------------------------------------------------------
# Name:        Test for the overwriting hosted feature layer items using the 
#              update and publish methods of the Item class. Multiple feature
#              layers are published with various source item types. Each source
#              item is updated with a new file then publish is called with the
#              overwrite argument. Output types confirmed.
# Purpose:     Integration tests for overwriting items with the Item.publish
#              method of the ArcGIS Python API.
# -----------------------------------------------------------------------------

import unittest
import time
import pandas as pd

from integration.config import (
    get_resource_path
)
from utils.decorators import integration_test, profiles
from utils.data_utils import (
    add_source_item,
    publish_test_item,
    cleanup_published_items,
    cleanup_folders
)

from arcgis.gis import GIS, ItemTypeEnum

def setUpModule():
    import warnings
    warnings.filterwarnings("ignore")

@profiles.admin_all
@integration_test
class Test_Item_overwrite_publish_source_item(unittest.TestCase):
    """
    Test to check if a Item object works with ArcGIS Online org
    """

    @classmethod
    def setUpClass(cls):
        """
        Use data utilities to publish multiple feature layers from the same csv
        source item to verify overwrite failure after updating csv item. Also,
        publish feature layers from a csv, file geodatabase, service definition,
        and shapefile item respectively and test each for overwrite after updating
        source item.
        """
        print("\n======= begin setUpClass ====================================\n")
        
        cls.item_test_overwrite_folder = cls.gis.content.folders._get_or_create(
            "aa_item_overwrite_ntgrtn_tests"
        )

        # add csv item and publish feature layer from it
        cls.one_to_many_csv_source = get_resource_path(
            relative_path="staging_data/item_class_test_data/set1_overwrite_manyHFS_csv.csv",
            verify=True,
            unique_copy=True
        )

        cls.one_to_many_wfl_item = publish_test_item(
            gis=cls.gis,
            layer_name="set1_overwrite_manyHFS_csv",
            item_type=ItemTypeEnum.CSV,
            source_data_path=cls.one_to_many_csv_source,
            folder=cls.item_test_overwrite_folder,
        )
        cls.one_to_many_csv_item = cls.one_to_many_wfl_item.related_items("Service2Data", "forward")[0]
          
        # publish a second feature layer from same csv item above to confirm
        # Runtime Error when attempting to overwrite a csv item from which
        # multiple items are published
        cls.one_to_many_wfl_item_1 = cls.one_to_many_csv_item.publish(
            publish_parameters={"name": "set1_overwrite_manyHFS_csv_1"}
        )
        cls.assertIsNotNone(
            cls.one_to_many_wfl_item_1, "Cannot publish CSV into a feature service"
        )
        cls.one_to_many_wfl_item_1.update({"title": "set1_overwrite_manyHFS_csv_1"})

        # publish a third Feature Layer from the same csv item
        cls.one_to_many_wfl_item_2 = cls.one_to_many_csv_item.publish(
                publish_parameters={"name": "set1_overwrite_manyHFS_csv_2"}
        )
        cls.assertIsNotNone(
            cls.one_to_many_wfl_item_2, "Cannot publish CSV into a feature service"
        )
        cls.one_to_many_wfl_item_2.update({"title": "set1_overwrite_manyHFS_csv_2"})

        # add new csv item and publish feature layer for overwrite test
        cls.csv2_source_file = get_resource_path(
            relative_path="staging_data/item_class_test_data/set1_overwrite_HFS_csv2.csv",
            verify=True,
            unique_copy=True
        )

        cls.set1_overwrite_HFS_csv2 = publish_test_item(
            gis=cls.gis,
            layer_name="set1_overwrite_HFS_csv2",
            item_type=ItemTypeEnum.CSV,
            source_data_path=cls.csv2_source_file,
            folder=cls.item_test_overwrite_folder
        )

        cls.csv2_source_csv_item = cls.set1_overwrite_HFS_csv2.related_items("Service2Data", "forward")[0]

        # add a csv item to test updating the source file
        cls.csv_path = get_resource_path(
            relative_path="staging_data/item_class_test_data/set1_overwrite_old.csv",
            verify=True,
            unique_copy=True
        )
    
        cls.csv_item = add_source_item(
            gis=cls.gis,
            layer_name="set1_overwrite_old",
            item_type=ItemTypeEnum.CSV,
            source_data_path=cls.csv_path,
            folder=cls.item_test_overwrite_folder,
        )
        
        # add a file geodatabase item and publish feature layer from it
        cls.fgdb_source_path = get_resource_path(
            relative_path="staging_data/item_class_test_data/set1_HFS_fgdb.gdb.zip",
            verify=True,
            unique_copy=True
        )

        cls.flyr_from_fgdb_item = publish_test_item(
            gis=cls.gis,
            layer_name="set1_HFS_fgdb_gdb",
            item_type=ItemTypeEnum.FILE_GEODATABASE,
            source_data_path=str(cls.fgdb_source_path),
            folder=cls.item_test_overwrite_folder,
        )
        cls.fgdb_source_item = cls.flyr_from_fgdb_item.related_items("Service2Data", "forward")[0]
        
        # add a service definition item and publish feature layer from it
        if not cls.gis._is_arcgisonline:
            cls.source_sd_file = get_resource_path(
                relative_path="staging_data/item_class_test_data/us_capitals_sd.sd",
                verify=True,
                unique_copy=True
            )
            cls.sd_flyr_item = publish_test_item(
                gis=cls.gis,
                layer_name="us_capitals_sd",
                item_type=ItemTypeEnum.SERVICE_DEFINITION,
                source_data_path=cls.source_sd_file,
                folder=cls.item_test_overwrite_folder
            )
            cls.source_sd_item = cls.sd_flyr_item.related_items("Service2Data", "forward")[0]
        else:
            cls.source_sd_file = get_resource_path(
                relative_path="staging_data/item_class_test_data/us_states_rivers.sd",
                verify=True,
                unique_copy=True
            )
            cls.sd_flyr_item = publish_test_item(
                gis=cls.gis,
                layer_name="us_states_rivers_sd",
                item_type=ItemTypeEnum.SERVICE_DEFINITION,
                source_data_path=cls.source_sd_file,
                folder=cls.item_test_overwrite_folder
            )
            cls.source_sd_item = cls.sd_flyr_item.related_items("Service2Data", "forward")[0]
        
        # add a shapefile item and publish feature layer from it
        cls.shp_source_file = get_resource_path(
            relative_path = "staging_data/item_class_test_data/set1_Item_overwrite_HFS_shp.zip",
            verify=True,
            unique_copy=True
        )
        cls.shp_flyr_item = publish_test_item(
            gis=cls.gis,
            item_type=ItemTypeEnum.SHAPEFILE,
            layer_name="set1_Item_overwrite_HFS_shp",
            source_data_path=cls.shp_source_file,
            folder=cls.item_test_overwrite_folder,
        )
        cls.shp_source_item = cls.shp_flyr_item.related_items("Service2Data", "forward")[0]        
        
        print("\n======= begin setUpClass ====================================\n")
        print("Beginning tests in Test_Item_agol class\n")

    @classmethod
    def tearDownClass(cls):
        print("\n================ begin tearDownClass ========================\n")
        test_items = list(cls.item_test_overwrite_folder.list())
        if test_items:
            cleanup_published_items(test_items)
        else:
            print(f"Test items already cleared from test folder.")
        cleanup_folders(
            gis=cls.gis,
            folder_names=[cls.item_test_overwrite_folder.name]
        )
        print("\n================ end tearDownClass ==========================\n")
        
    def setUp(self):
        print(f"\n{'-' * 40}\nTest: starting {self._testMethodName}...")
        self._start_time = time.time()
        
    def tearDown(self):
        elapsed_time = time.time() - self._start_time
        print(f"{' ' * 4}...test took {elapsed_time / 60:.2f} minutes.\n")    
        
    def test_overwrite_csv_item_source(self):
        """
        Update a csv item with new csv file and ensure the contents are updated
        while the itemid remains the same.
        """
        self.assertIsNotNone(self.csv_item, "CSV item not found and not added.")

        old_csv_data = self.csv_item.download()

        old_df = pd.read_csv(old_csv_data)
        self.assertEqual(len(old_df), 10, "Original csv file does not have 10 records.")
        old_item_id = self.csv_item.id

        # update csv item
        new_csv_path = get_resource_path(
            relative_path="staging_data/item_class_test_data/overwrite_data/set1_overwrite_new.csv",
            verify=True,
            unique_copy=True
        )

        item_update_result = self.csv_item.update({}, data=new_csv_path)

        self.assertTrue(
            item_update_result, "Calling update on csv item does not return True"
        )
        
        new_item_id = self.csv_item.id

        self.assertEqual(
            old_item_id,
            new_item_id,
            "CSV item ID is not same after updating csv data."
        )
        
        csv_download_path = self.csv_item.download()

        new_df = pd.read_csv(new_csv_path)
        downloaded_file_df = pd.read_csv(csv_download_path)
        self.assertEqual(
            new_df.shape,
            downloaded_file_df.shape,
            "The number of rows and columns in CSV item not updated with new csv data.",
        )
        self.assertGreater(
            len(new_df),
            len(old_df),
            "The number of records in CSV item was not updated properly."
        )
        
    def test_overwrite_manyHFS_using_csv_errors(self):
        """
        Multiple feature layers are published from the same csv item. Updating
        the csv item with a new csv file and then attempting to publish with
        overwrite should raise RunTime Error.
        """
        if not self.one_to_many_csv_item:
            self.skipTest("One to many csv item failed to publish in setUpClass.")

        new_csv_path = get_resource_path(
            relative_path="staging_data/item_class_test_data/overwrite_data/set1_overwrite_manyHFS_csv.csv",
            verify=True,
            unique_copy=True
        )

        item_update_result = self.one_to_many_csv_item.update(
            {}, data=new_csv_path
        )
        self.assertTrue(
            item_update_result, "Calling update on csv item does not return True"
        )

        # overwrite the feature layer
        with self.assertRaises(RuntimeError):
            self.one_to_many_csv_item.publish(overwrite=True)
    
    def test_overwrite_HFS_using_csv(self):
        """
        Update the csv file for a csv item that was used to publish a feature
        layer item. Then overwrite the feature layer with the publish method
        on the csv item. Ensure the contents are updated and the item id
        remains the same.
        """

        csv_item = self.csv2_source_csv_item
        if not csv_item:
            self.skipTest("Source csv item failed to publish in setUpClass.")

        orig_csv_item_id = csv_item.id

        orig_wfl_item = self.set1_overwrite_HFS_csv2
        if not orig_wfl_item:
            self.skipTest("Feature Layer failed to publish in setUpClass.")
        
        orig_wflayer = orig_wfl_item.layers[0]
        orig_num_features = orig_wflayer.query(return_count_only=True)

        new_csv_path = get_resource_path(
            relative_path="staging_data/item_class_test_data/overwrite_data/set1_overwrite_HFS_csv2.csv",
            verify=True,
            unique_copy=True
        )
        item_update_result = csv_item.update({}, data=new_csv_path)
        self.assertTrue(
            item_update_result, "Calling update on csv item does not return True"
        )
        self.assertEqual(
            orig_csv_item_id,
            csv_item.id,
            "Item id changed after calling update."
        )

        overwrite_result = csv_item.publish(overwrite=True)
        self.assertIsNotNone(
            overwrite_result, "Calling publish with overwrite True returns None"
        )
        new_wfl_item_id = overwrite_result.id

        self.assertEqual(
            orig_wfl_item.id,
            new_wfl_item_id,
            "Item ID is not same after overwriting",
        )

        flayer = overwrite_result.layers[0]
        fset = flayer.query()
        overwritten_flayer_df = fset.sdf

        self.assertGreater(
            len(overwritten_flayer_df),
            orig_num_features,
            "Number of rows did not increase after overwriting per expectation",
        )

    def test_overwrite_HFS_using_fgdb(self):
        """
        Update the fgdb file for a fgdb item that was used to publish a feature
        layer item. Then overwrite the feature layer with the publish method
        on the fgdb item. Ensure the contents are updated and the item id
        remains the same.
        """

        orig_flyr_from_fgdb_item = self.flyr_from_fgdb_item
        if not orig_flyr_from_fgdb_item:
            self.skipTest("Feature Layer from FGDB failed to publish in setUpClass.")

        orig_fgdb_source_item = self.fgdb_source_item
        if not orig_fgdb_source_item:
            self.skipTest("Source fdgb item failed to publish in setUpClass.")

    
        orig_flyr_id = orig_flyr_from_fgdb_item.id
        orig_flayer = orig_flyr_from_fgdb_item.layers[0]
        orig_fset = orig_flayer.query()
        orig_flayer_df = orig_fset.sdf

        orig_num_features = len(orig_flayer_df)

        new_fgdb_path = get_resource_path(
            relative_path="staging_data/item_class_test_data/overwrite_data/set1_Item_overwrite_HFS_fgdb.gdb.zip",
            verify=True,
            unique_copy=True
        )

        item_update_result = orig_fgdb_source_item.update({}, data=new_fgdb_path)
        self.assertTrue(
            item_update_result, 
            "Calling update on fgdb item does not return True"
        )

        # overwrite the feature layer
        overwrite_result = orig_fgdb_source_item.publish(overwrite=True)

        self.assertIsNotNone(
            overwrite_result, 
            "Calling publish with overwrite True returns None"
        )
        new_wfl_item_id = overwrite_result.id

        self.assertEqual(
            orig_flyr_id,
            new_wfl_item_id,
            "Item ID is not same after overwriting",
        )

        flayer = overwrite_result.layers[0]
        fset = flayer.query()
        overwritten_flayer_df = fset.sdf

        self.assertGreater(
            len(overwritten_flayer_df),
            orig_num_features,
            "Number of rows did not increase after overwriting per expectation",
        )

    def test_overwrite_HFS_using_shp(self):
        """
        Update the shapefile for a shapefile item that was used to publish a feature
        layer item. Then overwrite the feature layer with the publish method
        on the shapefile item. Ensure the contents are updated and the item id
        remains the same.
        """
        if not self.shp_flyr_item:
            self.skipTest("Feature Layer not published from shapefile.")

        orig_shp_flyr_item_id = self.shp_flyr_item.id
        orig_flayer = self.shp_flyr_item.layers[0]
        orig_fset = orig_flayer.query()
        orig_flayer_df = orig_fset.sdf

        orig_num_features = len(orig_flayer_df)

        # update shp item
        new_shp_path = get_resource_path(
            relative_path="staging_data/item_class_test_data/overwrite_data/set1_Item_overwrite_HFS_shp.zip",
            verify=True,
            unique_copy=True
        )

        item_update_result = self.shp_source_item.update({}, data=new_shp_path)
        self.assertTrue(
            item_update_result, 
            "Calling update on shp item does not return True"
        )

        overwrite_result = self.shp_source_item.publish(
            overwrite=True
        )
        self.assertIsNotNone(
            overwrite_result, "Calling publish with overwrite True returns None"
        )
        new_wfl_item_id = overwrite_result.id

        self.assertEqual(
            orig_shp_flyr_item_id,
            new_wfl_item_id,
            "Item ID is not same after overwriting",
        )

        flayer = overwrite_result.layers[0]
        fset = flayer.query()
        overwritten_flayer_df = fset.sdf

        self.assertGreater(
            len(overwritten_flayer_df),
            orig_num_features,
            "Number of rows needs to be more after overwriting",
        )

    def test_overwrite_HFS_using_sd(self):
        """
        Update the service definition file for a service definition item that
        was used to publish a feature layer item. Then overwrite the feature
        layer with the publish method on the service definition item. Ensure
        the contents are updated while the item id remains the same.
        """

        self.assertIsNotNone(
            self.sd_flyr_item,
            "Feature Layer not published from service defintion."
        )
        orig_fl_item_id = self.sd_flyr_item.id
        orig_num_layers = len(self.sd_flyr_item.layers)

        if not self.gis._is_arcgisonline:
            new_sd_path = get_resource_path(
                relative_path="staging_data/item_class_test_data/overwrite_data/us_capitals_sd.sd",
                verify=True,
                unique_copy=True
            )
        else:
            new_sd_path = get_resource_path(
                relative_path="staging_data/item_class_test_data/overwrite_data/us_states_rivers.sd",
                verify=True,
                unique_copy=True
            )
        item_update_result = self.source_sd_item.update({}, data=new_sd_path)
        self.assertTrue(
            item_update_result, "Calling update on sd item does not return True"
        )

        overwrite_result = self.source_sd_item.publish(overwrite=True)
        self.assertIsNotNone(
            overwrite_result, "Calling publish with overwrite True returns None"
        )
        new_wfl_item_id = overwrite_result.id

        self.assertEqual(
            orig_fl_item_id,
            new_wfl_item_id,
            "Item ID is not same after overwriting",
        )

        if not self.gis._is_arcgisonline:
            self.assertGreater(
                len(overwrite_result.layers),
                orig_num_layers,
                "Number of layers needs to be more after overwriting"
            )
        else:
            self.assertLess(
                len(overwrite_result.layers),
                orig_num_layers,
                "Number of layers needs to be fewer after overwriting",
            )
            
if __name__ == "__main__":
    unittest.main()