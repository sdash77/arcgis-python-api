# -------------------------------------------------------------------------------
# Name:        Item class tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
import time

from integration.config import (
    get_resource_path,
    get_web_resource_path
)
from utils.decorators import integration_test, profiles
from utils.data_utils import publish_test_item, cleanup_published_items, cleanup_folders

from arcgis.gis import ItemTypeEnum, Item, GIS
from arcgis.layers import VectorTileLayer


# @profiles.admin_kubernetes
@integration_test
class Test_Item_arcgis_kubernetes(unittest.TestCase):
    """
    Test to check if a Item object works with ArcGIS Enterprise on Kubernetes.
    """
    @classmethod
    def setUpClass(cls):
        """
        Check if portal can be reached
        Get class test asset location
        :return:
        """
        # devet00110.esri.com/arcgis - 12.0
        # cls.gis = GIS(
        #     profile="k8s_12"
        # )
        # Kubernetes 12.0 - Build 7056
        cls.gis = GIS(
            url="https://rqa01bi-rqa01bi.apps.openshift416release.esri.com/gis/home",
            username="PAPIadmin",
            password="PAPIletmein01"
        )

        if cls.gis is None:
            unittest.skipTest("Skipping tests as GIS object is None")

        cls.item_test_folder = cls.gis.content.folders._get_or_create(
            "aa_item_ntgrtn_tests"
        )

        try:
            cls.one_to_many_wfl_item = [
                i for i in cls.gis.content.search(
                "set1_overwrite_manyHFS *", "Feature Layer"
            ) if i.title.endswith("_csv")
            ][0]
            cls.one_to_many_csv_item = cls.one_to_many_wfl_item.related_items("Service2Data", "forward")[0]
        except IndexError as ie:
            cls.csv_source_path = get_resource_path(
                relative_path="staging_data/item_class_test_data/set1_overwrite_manyHFS_csv.csv",
                verify=True,
                unique_copy=True
            )

            cls.one_to_many_wfl_item = publish_test_item(
                gis=cls.gis,
                layer_name="set1_overwrite_manyHFS_csv",
                item_type=ItemTypeEnum.CSV,
                source_data_path=cls.csv_source_path,
                prep_for_editing=False,
                folder=cls.item_test_folder
            )
            cls.one_to_many_csv_item = cls.one_to_many_wfl_item.related_items("Service2Data", "forward")[0]
        
        cls.assertIsNotNone(
            cls.one_to_many_wfl_item,
            "Failed to get Feature Layer for csv overwrite tests."
        )
       
        try:
            cls.one_to_many_wfl_item_1 = [
                i1 for i1 in cls.gis.content.search(
                "set1_overwrite_manyHFS_csv *", "Feature Layer"
                ) if i1.title.endswith("_csv_1")
            ][0]
            cls.one_to_many_csv_item1 = cls.one_to_many_wfl_item_1.related_items("Service2Data", "forward")[0]
        except IndexError as ie:
            cls.one_to_many_wfl_item_1 = cls.one_to_many_csv_item.publish(
                publish_parameters={"name": "set1_overwrite_manyHFS_csv_1"} 
            )
            cls.assertIsNotNone(
                cls.one_to_many_wfl_item_1, "Cannot publish CSV into a feature service"
            )
            cls.one_to_many_wfl_item_1.update({"title": "set1_overwrite_manyHFS_csv_1"})

        try:
            cls.one_to_many_wfl_item_2 = [
                i2 
                for i2 in cls.gis.content.search(
                    "set1_overwrite_manyHFS_csv *", 
                    "Feature Layer"
                ) if i2.title.endswith("_csv_2")
            ][0]
            cls.one_to_many_csv_item2 = cls.one_to_many_wfl_item_2.related_items("Service2Data", "forward")[0]
        except IndexError as ie:
            cls.one_to_many_wfl_item_2 = cls.one_to_many_csv_item.publish(
                publish_parameters={"name":"set1_overwrite_manyHFS_csv_2"}
            )
            cls.assertIsNotNone(
                cls.one_to_many_wfl_item_2,
                "Cannot publish CSV into a feature service"
            )
            cls.one_to_many_wfl_item_2.update({"title": "set1_overwrite_manyHFS_csv_2"})

        try:
            cls.one_to_one_wfl_item = [
                i for i in cls.gis.content.search(
                "set1_overwrite_HFS *", "Feature Layer")
                if i.title.endswith("_csv2")
            ][0]
            cls.one_to_one_csv_item = cls.one_to_one_wfl_item.related_items("Service2Data", "forward")[0]
        except IndexError as ie:
            cls.csv_source_file = get_resource_path(
                relative_path="staging_data/item_class_test_data/set1_overwrite_HFS_csv2.csv",
                verify=True,
                unique_copy=True
            )
            cls.one_to_one_wfl_item = publish_test_item(
                gis=cls.gis,
                layer_name="set1_overwrite_HFS_csv2",
                item_type=ItemTypeEnum.CSV,
                source_data_path=cls.csv_source_file,
                folder=cls.item_test_folder
            )
            cls.one_to_one_csv_item = cls.one_to_one_wfl_item.related_items("Service2Data", "forward")[0]

        try:
            cls.shp_lyr_item = [
                si
                for si in cls.gis.content.search("title:Arkansas *", "Feature Layer")
                if si.title.endswith("hospitals")
            ][0]
            cls.shp_item = cls.shp_lyr_item.related_items("Service2Data", "forward")[0]
        except IndexError as ie:
            cls.shp_source_data = get_resource_path(
                relative_path="staging_data/item_class_test_data/ar_hospitals.zip",
                verify=True,
                unique_copy=True
            )

            cls.shp_lyr_item = publish_test_item(
                gis=cls.gis,
                layer_name="Arkansas_hospitals",
                item_type=ItemTypeEnum.SHAPEFILE,
                source_data_path=cls.shp_source_data,
                folder=cls.item_test_folder
            )
            cls.shp_item = cls.shp_lyr_item.related_items("Service2Data", "forward")[0]

        # region print banner
        print("==================================================================")
        print("Beginning tests in Test_Item_kubernetes_builtin class")
        # endregion

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")
        test_items = list(cls.item_test_folder.list())
        cleanup_published_items(items=test_items)
        cleanup_folders(
            gis=cls.gis,
            folder_names=[cls.item_test_folder.name]
        )

    def test_publish_vtpk(self):       
        try:
            vtl_item = [
                vt
                for vt in self.gis.content.search("set2_vtpk_world *", "Tile Layer")
                if vt.type == "Vector Tile Service"
            ][0]
        except IndexError as ie:
            vtl_package_file = get_web_resource_path(
                relative_path="data/set2_vtpk_worldgreen.vtpk",
                unique_copy=True
            )
                
            vtl_item = publish_test_item(
                gis=self.gis,
                layer_name="set2_vtpk_worldgreen",
                item_type=ItemTypeEnum.VECTOR_TILE_PACKAGE,
                source_data_path=vtl_package_file,
                folder=self.item_test_folder
            )
            vtl_package_item = vtl_item.related_items("Service2Data", "forward")[0]
        except Exception as e:
            print("Failed to get or publish vector tile layer.")
            print(str(e))
        
        self.assertIsNotNone(vtl_item, "No vector tile layer exists for test.")
        self.assertEqual(
            vtl_item.type,
            "Vector Tile Service",
            "Publishing VTPK does not create an item of type Vector Tile Service",
        )
        self.assertEqual(
            len(vtl_item.layers), 1, "No layers found in Vector Tile Service"
        )
        self.assertEqual(
            vtl_item.title,
            "set2_vtpk_worldgreen",
            "Title of published item does not match",
        )
        self.assertIsInstance(
            vtl_item.layers[0],
            VectorTileLayer,
            "Layer type not published as a Vector Tile Layer.",
        )
        self.assertEqual(
            vtl_package_item.type,
            "Vector Tile Package",
            "Vector tile data item is not vector tile package as expe"
        )

    def test_publish_slpk(self):
        try:
            scn_lyr_item = [
                sc
                for sc in self.gis.content.search("set2_slpk *", "Scene Layer")
                if sc.title.endswith("Vancouver")
            ][0]
            scn_pkg_item = scn_lyr_item.related_items("Service2Data", "forward")[0]
        except IndexError as ie:
            slpk_package_file = get_web_resource_path(
                relative_path=r"data/set2_slpk_Vancouver.slpk",
                unique_copy=True
            )

            scn_lyr_item = publish_test_item(
                gis=self.gis,
                layer_name="set2_slpk_Vancouver",
                item_type=ItemTypeEnum.SCENE_PACKAGE,
                source_data_path=slpk_package_file,
                folder=self.item_test_folder
            )
            time.sleep(120)  # wait for the item to be processed

        self.assertIsInstance(
            scn_lyr_item,
            Item,
            "Scene layer item not found or not published.",
        )

        self.assertEqual(
            scn_lyr_item.type,
            "Scene Service",
            "Publishing SLPK does not create an item of type Scene Service",
        )

        self.assertTrue(
            len(scn_lyr_item.layers) > 0, "No layers found in Scene Service"
        )

    def test_publish_tpkx(self):
        try:
            tile_lyr = [
                it 
                for it in self.gis.content.search("title: Riverside *", "Tile Layer")
                if it.title.endswith("side")
            ][0]
            tile_pkg_item = tile_lyr.related_items("Service2Data", "forward")[0]
        except IndexError as ie:
            tpkx_package_file = get_web_resource_path(
                relative_path="data/Riverside.tpkx",
                unique_copy=True
            )

            tile_lyr = publish_test_item(
                gis=self.gis,
                layer_name="Riverside",
                item_type=ItemTypeEnum.TILE_PACKAGE,
                source_data_path=tpkx_package_file,
                folder=self.item_test_folder
            )
            tile_pkg_item = tile_lyr.related_items("Service2Data", "forward")[0]

        self.assertIsNotNone(
            tile_lyr,
            "Failed to find tile layer or publish TPKX item."
        )
      
        self.assertIsInstance(
            tile_lyr,
            Item,
            "Tile layer is not an item."
        )

        self.assertEqual(
            tile_lyr.type,
            "Map Service",
            "Publishing TPKX does not create Map Service item."
        )
        self.assertEqual(
            tile_pkg_item.type,
            "Tile Package",
            "Related data item to Map Service is not tile package."
        )

    def test_publish_shp(self):
        try:
            shp_lyr_item = [
                si
                for si in self.gis.content.search("title:Arkansas *", "Feature Layer")
                if si.title.endswith("boundaries")
            ][0]
            shp_item = shp_lyr_item.related_items("Service2Data", "forward")[0]
        except IndexError as ie:
            shp_source_data = get_web_resource_path(
                relative_path="data/AR_Boundaries.zip",
                unique_copy=True
            )

            shp_lyr_item = publish_test_item(
                gis=self.gis,
                layer_name="Arkansas_boundaries",
                item_type=ItemTypeEnum.SHAPEFILE,
                source_data_path=shp_source_data,
                folder=self.item_test_folder
            )
            shp_item = shp_lyr_item.related_items("Service2Data", "forward")[0]
        
        if not shp_lyr_item:
            self.skipTest("No layer published from shapefile.")

        self.assertIsInstance(
            shp_lyr_item,
            Item,
            "Publishing zipped shapefile failed to result in item."
        )
        self.assertEqual(
            shp_lyr_item.type,
            "Feature Service",
            "Publishing SHP does not create an item of type Feature Service",
        )
        self.assertEqual(
            shp_item.type,
            "Shapefile",
            "Shapefile item related data item is not a shapefile."
        )
        self.assertTrue(
            len(shp_lyr_item.layers) > 0, 
            "No layers found in Feature Service published from shapefile."
        )
        self.assertGreater(
            shp_lyr_item.layers[0].query(return_count_only=True),
            0,
            "Feature layer created from shapefile has no features."
        )

    def test_publish_fgdb(self):
        orig_cities_lyr_item = [
            fi
            for fi in self.gis.content.search("set2_USA *", "Feature Layer")
            if fi.title.endswith("USAcities")
        ]
        if orig_cities_lyr_item:
            try:
                for city_item in orig_cities_lyr_item:
                    orig_cities_fgdb_item = city_item.related_items("Service2Data", "forward")[0]
                    orig_cities_fgdb_item.delete()
                city_item.delete()
            except Exception as e:
                self.skipTest("Failed to delete previous feature layer item and file geodatabase item.")
        try:
            cities_fgdb_source = get_resource_path(
                relative_path="staging_data/item_class_test_data/set2_USAcities.zip",
                verify=True,
                unique_copy=True
            )          
            cities_lyr_item = publish_test_item(
                gis=self.gis,
                layer_name="set2_USAcities",
                item_type=ItemTypeEnum.FILE_GEODATABASE,
                source_data_path=cities_fgdb_source,
                folder=self.item_test_folder
            )
        except Exception as e:
            print(str(e))
            self.skipTest("Failed to publish feature layer from file geodatabase.")
        finally:
            if not cities_lyr_item:
                self.skipTest("Failed to publish feature layer item from geodatabase.")
  
        self.assertIsInstance(
            cities_lyr_item,
            Item,
            "Failed to publish Item from zipped file geodatabase."
        )
        self.assertEqual(
            cities_lyr_item.type,
            "Feature Service",
            "Publishing zipped file geodatabase does not create a feature service."
        )
        self.assertEqual(
            len(cities_lyr_item.layers),
            1, 
            "No feature layers found in published feature service."
        )        
        self.assertGreater(
            len(cities_lyr_item.layers[0].query().features),
            0,
            "No features found in published feature service."
        )

    def test_publish_flyr_sd(self):
        sd_flyr_items = [
                si
                for si in self.gis.content.search(
                    "us_capitals *", item_type="Feature Layer", max_items=1
                ) if si.title.endswith("_sd")
            ]
        if sd_flyr_items:
            try:
                for sd_lyr in sd_flyr_items:
                    sd_item = sd_lyr.related_items("Service2Data", "forward")[0]
                    sd_item.delete()
                sd_lyr.delete()
            except Exception as e:
                print(str(e))
                self.skipTest("Failed to delete previous test layer item published from service definition item.")
        try:
            sd_source_file = get_resource_path(
                relative_path="staging_data/item_class_test_data/us_capitals_sd.sd",
                verify=True,
                unique_copy=True
            )
            sd_lyr_item = publish_test_item(
                gis=self.gis,
                layer_name="US_capitals_sd",
                item_type=ItemTypeEnum.SERVICE_DEFINITION,
                source_data_path=sd_source_file,
                folder=self.item_test_folder
            )
            sd_item = sd_lyr_item.related_items("Service2Data", "forward")[0]
        except Exception as e:           
            print(str(e))
            self.skipTest("Failed to publish layer from service definition item.")  
        finally:
            if not sd_lyr_item:
                self.skipTest("Failed to publish feature layer and service definition file items.")
        
        self.assertIsInstance(
            sd_lyr_item,
            Item,
            "Publish opertaion did not result in an item."
        )
        self.assertEqual(
            sd_lyr_item.type,
            "Feature Service",
            "Publishing service definition does not create Feature Service item.",
        )
        self.assertEqual(
            sd_item.type,
            "Service Definition",
            "Feature layer related data item is not a service definition item as expected."
        )
        self.assertTrue(
            len(sd_lyr_item.layers) == 2,
            "Publishing item did not create 2 layers as expected in Feature Service."
        )
        self.assertGreater(
            sd_lyr_item.layers[0].query(return_count_only=True),
            0,
            "Layer created from service definition has no features."
        )

    @unittest.skip("Bug: Issue #13033")
    def test_create_tile_lyr_from_feature_lyr(self):
        flyr_item = self.shp_lyr_item
        if not flyr_item:
            self.skipTest("No feature layer item to create tile layer from.")

        tile_lyr_item_f = flyr_item.create_tile_service(
            title="AR_hospital_tiles",
            min_scale=9244649, 
            max_scale=2311162,
            build_cache=True
        )
        self.assertTrue(
            tile_lyr_item_f,
            "Failed to publish tile layer from feature layer item."
        )
        self.assertEqual(
            tile_lyr_item_f.type,
            "Map Service",
            "Failed to publish type Map Service when creating tile layer from feature layer item."

        )
  
    def test_overwrite_manyHFS_using_csv_errors(self):
        """
        Multiple feature layers are published using the same csv. Updating the csv 
        file and attempting to overwrite should raise RunTime Error.
        :return:
        """
        # update csv item
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
        Publish a feature layer with csv.
        Update the csv and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        csv_item = self.one_to_one_csv_item
        if not csv_item:
            self.skipTest("Source csv item failed to publish in setUpClass.")

        orig_csv_item_id = csv_item.id

        orig_wfl_item = self.one_to_one_wfl_item
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

        try:
            overwrite_result = csv_item.publish(overwrite=True)
        except Exception as e:
            self.skipTest(f"Failed to overwrite feature layer from updated csv item: {str(e)}")

        self.assertIsNotNone(
            overwrite_result, "Calling publish with overwrite True returns None"
        )
        new_wfl_item_id = overwrite_result.id

        self.assertEqual(
            orig_wfl_item.id,
            new_wfl_item_id,
            "Item ID is not same after overwriting",
        )

        # verify content is updated
        flayer = overwrite_result.layers[0]
        fset = flayer.query()
        overwritten_flayer_df = fset.sdf

        self.assertGreater(
            len(overwritten_flayer_df),
            orig_num_features,
            "Number of rows did not increase after overwriting per expectation",
        )

if __name__ == "__main__":
    unittest.main()