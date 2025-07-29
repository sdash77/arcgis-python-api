# -------------------------------------------------------------------------------
# Name:        Item class tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
import time
import tempfile
from pathlib import Path
import pandas as pd

from integration.config import (
    get_resource_path,
    get_web_resource_path, 
    INTEGRATION_TEST_ITEM_TAG
)
from utils.decorators import integration_test, profiles
from utils.data_utils import (
    add_source_item,
    publish_test_item,
    cleanup_published_items,
    cleanup_folders
)

from arcgis.gis import ItemProperties, ItemTypeEnum, Item, GIS, ResourceManager
from arcgis.layers import VectorTileLayer, Object3DLayer, SceneLayer, MapFeatureLayer
from arcgis.features import FeatureLayer
from arcgis.map import Map

@profiles.admin_agol
@integration_test
class Test_Item_arcgis_online(unittest.TestCase):
    """
    Test to check if a Item object works with ArcGIS Online org
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal can be reached
        Get class test asset location
        :return:
        """

        cls.item_test_folder = cls.gis.content.folders._get_or_create(
            "aa_item_ntgrtn_tests"
        )


        try:
            cls.one_to_many_wfl_item =[
                i for i in cls.gis.content.search(
                    f"title:set1_overwrite_manyHFS * AND owner:{cls.gis.users.me.username}","Feature Layer")
                if i.title.endswith("_csv")
            ][0]
            cls.one_to_many_csv_item = cls.one_to_many_wfl_item.related_items("Service2Data", "forward")[0] 
            try:
                cls.one_to_many_wfl_item.move(cls.item_test_folder)
                cls.one_to_many_csv_item.move(cls.item_test_folder)
            except Exception as e:
                print("Cannot move item. Already exists in folder.")
                pass
        except IndexError as ie:
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
                folder=cls.item_test_folder,
            )
            cls.one_to_many_csv_item = cls.one_to_many_wfl_item.related_items("Service2Data", "forward")[0]

        try:
            cls.one_to_many_wfl_item_1 = [
                i2
                for i2 in cls.gis.content.search("set1_overwrite_manyHFS_csv_1", "Feature Layer")
                if i2.title.endswith("csv_1")
            ][0]
            try:
                cls.one_to_many_wfl_item_1.move(cls.item_test_folder)
            except Exception as e:
                print("Cannot move item. Already exists in folder.")
                pass
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
                i3
                for i3 in cls.gis.content.search(
                "set1_overwrite_manyHFS_csv *", "Feature Layer")
                if i3.title.endswith("csv_2")
            ][0]
            try:
                cls.one_to_many_wfl_item_2.move(cls.item_test_folder)
            except Exception as e:
                print("Cannot move item. Already exists in folder.")
                pass
        except IndexError as ie:
            cls.one_to_many_wfl_item_2 = cls.one_to_many_csv_item.publish(
                    publish_parameters={"name": "set1_overwrite_manyHFS_csv_2"}
            )
            cls.assertIsNotNone(
                cls.one_to_many_wfl_item_2, "Cannot publish CSV into a feature service"
            )
            cls.one_to_many_wfl_item_2.update({"title": "set1_overwrite_manyHFS_csv_2"})
        except Exception as e:
            print(str(e))

        try:
            cls.set1_overwrite_HFS_csv2 = [
                i 
                for i in cls.gis.content.search(
                    "set1_overwrite_HFS_csv2", "Feature Layer"
                ) if i.title.endswith("csv2")
            ][0]
            cls.csv2_source_csv_item = cls.set1_overwrite_HFS_csv2.related_items("Service2Data", "forward")[0] 
            if cls.set1_overwrite_HFS_csv2:
                try:
                    cls.set1_overwrite_HFS_csv2.related_items("Service2Data", "forward")[0].move(cls.item_test_folder)
                    cls.set1_overwrite_HFS_csv2.move(cls.item_test_folder)
                except Exception as e:
                    print("CSV items already exist in test folder.")  
        except IndexError as ie:
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
                folder=cls.item_test_folder
            )

            cls.csv2_source_csv_item = cls.set1_overwrite_HFS_csv2.related_items("Service2Data", "forward")[0]

        try:
            cls.flyr_from_fgdb_item = [
                fi
                for fi in cls.gis.content.search(
                "set1_HFS_fgdb *", "Feature Layer"
                ) if fi.title.endswith("_gdb")
            ][0]
            cls.fgdb_source_item = cls.flyr_from_fgdb_item.related_items(
                "Service2Data", "forward"
            )[0]
        except IndexError as ie:
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
                folder=cls.item_test_folder,
            )
            cls.fgdb_source_item = cls.flyr_from_fgdb_item.related_items("Service2Data", "forward")[0]

        try:
            cls.chicago_wfl_item = cls.gis.content.search(
                "Chicago_test_points", "Feature Layer"
            )[0]
            cls.chicago_source_data = cls.chicago_wfl_item.related_items(
                "Service2Data", "forward"
            )[0]
            cls.chicago_wfl_item.move(cls.item_test_folder)
            cls.chicago_source_data.move(cls.item_test_folder)
        except IndexError as ie:
            cls.chicago_source_data = get_resource_path(
                relative_path="staging_data/item_class_test_data/Chicago_points.csv",
                verify=True,
                unique_copy=True,
            )
            cls.chicago_wfl_item = publish_test_item(
                gis=cls.gis,
                layer_name="Chicago_test_points",
                item_type=ItemTypeEnum.CSV,
                source_data_path=cls.chicago_source_data,
                prep_for_editing=False,
                folder=cls.item_test_folder,
            )
        except Exception as me:
            if "Item already exists in target folder" in str(me):
                pass

        try:
            cls.chi_webmap = cls.gis.content.search(
                "chicago_webmap_downtest", "Web Map"
            )[0]
            cls.chi_webmap.move(cls.item_test_folder)
        except IndexError as ie:
            cls.chicago_map = cls.gis.map("Chicago")
            cls.chicago_map.content.add(cls.chicago_wfl_item)
            cls.chi_webmap = cls.chicago_map.save(
                item_properties={
                    "title": "chicago_webmap_downtest",
                    "tags": "ntgrtn-tst",
                    "snippet": "Web Map to test downloading",
                },
                folder=cls.item_test_folder.name,
            )
        except Exception as e:
            if "Item already exists in target folder" in str(e):
                pass
      
        print("==================================================================")
        print("Beginning tests in Test_Item_agol class\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")
        test_items = list(cls.item_test_folder.list())
        if test_items:
            cleanup_published_items(test_items)
        else:
            print(f"Test items already cleared from test folder.")
        cleanup_folders(
            gis=cls.gis,
            folder_names=[cls.item_test_folder.name]
        )
    
    def test_publish_vtpk(self):
        vtl_items = [
            vi
            for vi in self.gis.content.search(
                "set2_vtpk *", "Vector Tile Service"
            ) if vi.title.endswith("_worldgreen")
        ]

        if vtl_items:
            try:
                for vtl_item in vtl_items:
                    vtl_pkg_item = vtl_item.related_items("Service2Data", "forward")[0]
                    vtl_pkg_item.delete(permanent=True)
                vtl_item.delete(permanent=True)
            except Exception as e:
                self.skipTest("Failed to delete previous Vector Tile layer and package items.")

        vtpk_package_file = get_web_resource_path(
            relative_path="data/set2_vtpk_worldgreen.vtpk",
            unique_copy=True,
        )

        vtl_item = publish_test_item(
            gis=self.gis,
            layer_name="set2_vtpk_worldgreen",
            item_type=ItemTypeEnum.VECTOR_TILE_PACKAGE,
            source_data_path=vtpk_package_file,
            prep_for_editing=False,
            folder=self.item_test_folder,
        )
        vtpk_pkg_item = vtl_item.related_items("Service2Data", "forward")[0]

        self.assertIsNotNone(vtl_item, "Publish of vectory tile layer from VTPK item failed.")
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
            vtpk_pkg_item.type,
            "Vector Tile Package",
            "Data item for vector tile item is not vector tile package as expected."
        )

    def test_publish_spk(self):
        scn_items = [
            si
            for si in self.gis.content.search(
                "set2_spk *", item_type=ItemTypeEnum.SCENE_SERVICE.value
            ) if si.title.endswith("_SD3dbuildings")
        ]
        if scn_items:
            try:
                for scn_item in scn_items:
                    scn_pkg_item = scn_item.related_items("Service2Data", "forward")[0]
                    scn_pkg_item.delete(permanent=True)
                scn_item.delete(permanent=True)
            except Exception as e:
                self.skipTest("Failed to delete previous Scene Service and package items.") 

        spk_package_file = get_web_resource_path(
            relative_path="data/set2_spk_SD3dbuildings.spk",
            unique_copy=True
        )
        scn_item = publish_test_item(
            gis=self.gis,
            layer_name="set2_spk_SD3dbuildings",
            item_type=ItemTypeEnum.SCENE_PACKAGE,
            source_data_path=spk_package_file,
            folder=self.item_test_folder
        )
        scn_pkg_item = scn_item.related_items("Service2Data", "forward")[0]

        self.assertTrue(scn_item, f"Failed to publish Scene Service from {scn_pkg_item.title} {scn_pkg_item.type}.")
        self.assertIsInstance(
            scn_item, Item, f"Failed to publish {scn_pkg_item.title} Scene package."
        )
        self.assertEqual(
            scn_item.type,
            ItemTypeEnum.SCENE_SERVICE.value,
            f"{scn_item.title} is not a Scene Service item.",
        )
        self.assertEqual(
            len(scn_item.layers),
            1,
            "Failed to publish layer(s) for {scn_item.title} Scene.",
        )
        self.assertIsInstance(
            scn_item.layers[0],
            Object3DLayer,
            f"{scn_item.title} layer is not a SceneLayer as expected.",
        )

    def test_publish_slpk(self):
        slpk_lyr_items = [
            sli
            for sli in self.gis.content.search(
                "set2_slpk *", item_type=ItemTypeEnum.SCENE_SERVICE.value
            ) if sli.title.endswith("_Vancouver")
        ]

        if slpk_lyr_items:
            for slpk_lyr_item in slpk_lyr_items:
                slpk_pkg_item = slpk_lyr_item.related_items("Service2Data", "forward")[0]
                try:
                    slpk_pkg_item.delete(permanent=True)
                    slpk_lyr_item.delete(permanent=True)
                except Exception as e:
                    self.skipTest("Failed to delete previous Scene Layer and package items.")   
            
        slpk_package_file = get_web_resource_path(
            relative_path="data/set2_slpk_Vancouver.slpk",
            unique_copy=True
        )
        
        scn_pkg_item = self.item_test_folder.add(
            item_properties=ItemProperties(
                title="set2_slpk_Vancouver",
                item_type=ItemTypeEnum.SCENE_PACKAGE,
                snippet="Scene layer published from API integration test.",
                description="Vancouver scene published from slpk source file.",
                tags=INTEGRATION_TEST_ITEM_TAG
            ),
            file=slpk_package_file
        ).result()
        
        scn_item = scn_pkg_item.publish()
        
        self.assertTrue(scn_item, f"Failed to publish Scene Service from {scn_pkg_item.title} {scn_pkg_item.type}.")
        self.assertIsInstance(
            scn_item, Item, f"Failed to publish {scn_pkg_item.title} Scene package."
        )
        self.assertEqual(
            scn_item.type,
            ItemTypeEnum.SCENE_SERVICE.value,
            f"{scn_item.title} is not a Scene Service item.",
        )
        
        time.sleep(120)
        self.assertEqual(
            len(scn_item.layers),
            1,
            "Failed to publish layer(s) for {scn_item.title} Scene.",
        )
        self.assertIsInstance(
            scn_item.layers[0],
            Object3DLayer,
            f"{scn_item.title} layer is not a SceneLayer as expected.",
        )
        self.assertEqual(
            scn_pkg_item.type,
            "Scene Package",
            "Scene item related data item is not a scene package as expected."
        )

    def test_publish_tpk(self):    
        tile_lyr_items = [
            ti for ti in 
            self.gis.content.search(
                "set3_tpk *", item_type="Map Service", max_items=1
            ) if ti.title.endswith("tpk_SD")
        ]
        if tile_lyr_items:
            for tile_lyr_item in tile_lyr_items:
                tile_pkg_item = tile_lyr_item.related_items("Service2Data", "forward")[0]
                try:
                    tile_pkg_item.delete(permanent=True)
                    tile_lyr_item.delete(permanent=True)
                except Exception as e:
                    self.skipTest("Failed to delete previous Tile Layer and package items.")
        
        tile_pkg_file = get_web_resource_path(
            relative_path="data/set3_tpk_SD.tpk",
            unique_copy=True
        )

        tile_lyr_item = publish_test_item(
            gis=self.gis,
            layer_name="set3_tpk_SD",
            item_type=ItemTypeEnum.TILE_PACKAGE,
            source_data_path=tile_pkg_file,
            folder=self.item_test_folder
        )
        tile_pkg_item = tile_lyr_item.related_items("Service2Data", "forward")[0]

        self.assertTrue(tile_lyr_item, "Failed to publish tile layer from TPK item.")

        self.assertIsInstance(
            tile_lyr_item,
            Item,
            f"Publishing tpk item does not return an Item {tile_lyr_item.title}."
        )

        self.assertEqual(
            tile_lyr_item.type,
            "Map Service",
            "Publishing TPK does not create an Map Service item."
        )

        self.assertTrue(
            len(tile_lyr_item.layers) > 0, 
            "No layers published in Map Service."
        )
        self.assertEqual(
            tile_pkg_item.type,
            "Tile Package",
            "Tile layer item data item is not a tile package as expected."
        )

    def test_publish_flyr_sd(self):
        sd_flyr_items = [
           sdi
           for sdi in self.gis.content.search(
                "ago_multilyr_svc *", item_type="Feature Layer", max_items=1
           ) if sdi.title.endswith("_grplyr_map")
        ]
        
        if sd_flyr_items:
            for sd_flyr_item in sd_flyr_items: 
                try:
                    sd_item = sd_flyr_item.related_items("Service2Data", "forward")[0]
                    sd_item.delete(permanent=True)
                    sd_flyr_item.delete(permanent=True)
                except Exception as e:
                    self.skipTest("Failed to delete previous Feature Layer and package items.")
        
        sd_file = get_resource_path(
           relative_path="staging_data/item_class_test_data/ago_multilyr_svc_grplyr_x4j2.sd",
           verify=True,
           unique_copy=True
       )
       
        sd_flyr_item = publish_test_item(
            gis=self.gis,
            layer_name="ago_multilyr_svc_grplyr_map",
            item_type=ItemTypeEnum.SERVICE_DEFINITION,
            source_data_path=sd_file,
            folder=self.item_test_folder
        )
        sd_item = sd_flyr_item.related_items("Service2Data", "forward")[0]

        self.assertTrue(sd_flyr_item, "Failed to publish feature layer from service definition.")
        self.assertIsInstance(
            sd_flyr_item,
            Item,
            "Publish opertaion did not result in an item."
        )
        self.assertEqual(
            sd_flyr_item.type,
            "Feature Service",
            "Publishing service definition does not create Feature Service item.",
        )
        self.assertTrue(
            len(sd_flyr_item.layers) == 3, 
            "Publishing item did not create 3 layers as expected in Feature Service."
        )
        self.assertGreater(
            sd_flyr_item.layers[0].query(return_count_only=True),
            0,
            "Feature Service layer does not have features as expected."
        )

    def test_publish_tlyr_sd(self):
        sd_tlyr_items = [
            ti
            for ti in self.gis.content.search(
                "ago_Tiled *", item_type="Feature Layer", max_items=1
            ) if ti.title.endswith("_QueryLayer")
        ]
        if sd_tlyr_items:
            for sd_tlyr_item in sd_tlyr_items:
                try:
                    sd_titem = sd_tlyr_item.related_items("Service2Data", "forward")[0]
                    sd_titem.delete(permanent=True)
                    sd_tlyr_item.delete(permanent=True)
                except Exception as e:
                    self.skipTest("Failed to delete previous tile layer and service definition items.")

        sd_file = get_resource_path(
            relative_path="staging_data/item_class_test_data/agors_simpleTiled.sd",
            verify=True,
            unique_copy=True
        )

        sd_tile_pkg_item = self.item_test_folder.add(
            item_properties=ItemProperties(
                title="ago_Tile_QueryLayer",
                item_type=ItemTypeEnum.SERVICE_DEFINITION,
                snippet="Service definition item created with API.",
                description="Service definition used for integration testing.",
                tags=INTEGRATION_TEST_ITEM_TAG
            ),
            file=sd_file
        ).result()
        
        sd_tile_lyr_item = sd_tile_pkg_item.publish(
            build_initial_cache=True
        )
        
        time.sleep(180)
        self.assertTrue(sd_tile_lyr_item, "Failed to publish tile layer from service definition.")

        self.assertIsInstance(
            sd_tile_lyr_item,
            Item,
            "Publish opertaion did not result in an item."
        )

        self.assertEqual(
            sd_tile_lyr_item.type,
            "Map Service",
            "Publishing service definition does not create Feature Service item.",
        )

        self.assertTrue(
            len(sd_tile_lyr_item.layers) == 3,
            "Publishing item did not create 3 layers as expected in Map Service."
        )

    def test_publish_shp(self):
        shp_source_data = get_resource_path(
            relative_path="staging_data/USA_Major_Cities.zip",
             verify=True,
             unique_copy=True
        )
        shp_flyr_item = publish_test_item(
            gis=self.gis,
            layer_name="usa_major_cities_itemtest",
            item_type=ItemTypeEnum.SHAPEFILE,
            source_data_path=shp_source_data,
            prep_for_editing=False,
            folder=self.item_test_folder,
        )
        self.assertIsNotNone(shp_flyr_item, "Failed to publish shapefile layer.")
        self.assertEqual(
            len(shp_flyr_item.layers),
            1,
            "Shapefile layer item should have 1 layer."
        )
        self.assertGreater(
            shp_flyr_item.layers[0].query(return_count_only=True),
            0,
            "Shapefile layer does not have features as expected."
        )

    def test_resources_property(self):
        try:
            smap_item = self.gis.content.search(
                query="Giraffes *",
                item_type="StoryMap"
            )[0]
        except IndexError as ie:
            smap_item = self.gis.content.search(
                query=f"owner:{self.gis.users.me.username}",
                item_type="StoryMap"
            )[0]
        finally:
            if not smap_item:
                self.skipTest("No StoryMap items accessible for resource testing.")

        res_mgr = smap_item.resources

        self.assertIsInstance(
            res_mgr,
            ResourceManager,
            "The resources property did not return ResourceManager object."
        )

        self.assertGreater(
            len(res_mgr.list()),
            0,
            "StoryMap item has no resources as expected."
        )

        self.assertIsInstance(
            res_mgr.list()[0],
            dict,
            "Resource Manager list method does not return list of dictionaries as expected."
        )

        self.assertIn(
            res_mgr.list()[0]["resource"][-4:],
            ["json", "jpeg", "png"],
            "Story Map resource not in list of expected extensions."
        )

    def test_download_method_empty_data_outpath(self):
        """
        When Item has no data, Item.download() should download to a file of size 0
        :return:
        """
        try:
            chicago_wfl_item = self.gis.content.search("set1_Chicago", "Feature Layer")[
                0
            ]
            chicago_source_data = chicago_wfl_item.related_items("Service2Data", "forward")[0]
            chicago_wfl_item.move(self.item_test_folder)
            chicago_source_data.move(self.item_test_folder)
        except IndexError as ie:
            chicago_wfl_item = self.chicago_wfl_item
        except Exception as e:
            pass
        with tempfile.TemporaryDirectory() as temp_dir:
            chicago_data = chicago_wfl_item.download(save_path=temp_dir)
            chicago_data_size = Path(chicago_data).stat().st_size

        self.assertIsNotNone(
            chicago_data,
            "Calling download() on feature layer item with empty data resource throws error",
        )
        self.assertEqual(chicago_data_size, 0, "File size of feature layer download is > 0")

    def test_download_method_empty_data_nopath(self):
        """
        When Item has no data, Item.download() should download to a file of size 0
        :return:
        """
        try:
            chicago_wfl_item = self.gis.content.search("set1_Chicago", "Feature Layer")[
                0
            ]
            chicago_source_data = chicago_wfl_item.related_items("Service2Data", "forward")[0]
            chicago_wfl_item.move(self.item_test_folder)
            chicago_source_data.move(self.item_test_folder)
        except IndexError as ie:
            chicago_wfl_item = self.chicago_wfl_item
        except Exception as e:
            pass
        with tempfile.TemporaryDirectory() as temp_dir:
            chicago_data = chicago_wfl_item.download()
            chicago_data_size = Path(chicago_data).stat().st_size

        self.assertIsNotNone(
            chicago_data,
            "Calling download() on feature layer item with empty data resource throws error",
        )
        self.assertEqual(chicago_data_size, 0, "File size of empty item is > 0")

    def test_download_method_txt_data_nopath(self):
        """
        When no path is provided, Item.download() downloads to sys temp dir
        :return:
        """
       
        try:
            chicago_csv_item = self.chicago_wfl_item.related_items("Service2Data", "forward")[0]
        except IndexError as ie:
            self.skipTest("CSV item not returned as source for expected feature layer.") 
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chicago_data = chicago_csv_item.download()
            chicago_data_size = Path(chicago_data).stat().st_size

        self.assertIsInstance(
            chicago_data,
            str,
            "Calling download() on csv item does not return download str path",
        )
        self.assertTrue(
            Path(chicago_data).stem.startswith("Chicago_points"),
            "Download file name does not match known csv file name.",
        )
        self.assertGreater(
            chicago_data_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_download_method_txt_data_outputpath(self):
        """
        When given a download path, ensure Item.download() downloads file into that path
        :return:
        """
      
        try:
            chicago_csv_item = self.chicago_wfl_item.related_items("Service2Data", "forward")[0]
        except IndexError as ie:
            self.skipTest("CSV item not returned as source for expected feature layer.")

        with tempfile.TemporaryDirectory() as temp_dir:
            chicago_data = chicago_csv_item.download(save_path=temp_dir)
            chicago_data_size = Path(chicago_data).stat().st_size

        self.assertIsInstance(
            chicago_data,
            str,
            "Calling download() on csv item does not return download str path",
        )
        self.assertTrue(
            Path(chicago_data).stem.startswith("Chicago_points"),
            "Download file name does not match known input",
        )

        self.assertEqual(
            str(Path(chicago_data).parent),
            str(temp_dir),
            "Download path does not match temporary directory path."
        )
        
        self.assertGreater(
            chicago_data_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_download_method_JSON_data_outputpath(self):
        """
        When Item has JSON data, ensure Item.download() downloads file into that path instead
        of returning parsed dict
        :return:
        """
        
        JSON_item = self.chi_webmap
        if not JSON_item:
            unittest.skipTest("Web Map was not published as expected in setUpClass.")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = JSON_item.download(save_path=temp_dir)
            json_file_size = Path(json_file).stat().st_size

        self.assertIsInstance(
            json_file,
            str,
            "Calling download() on webmap item does not return download str path",
        )
        self.assertEqual(
            str(Path(json_file).parent),
            temp_dir,
            "Download file does not download to temporary directory.",
        )

        self.assertEqual(
            Path(json_file).stem,
            JSON_item.title,
            "Web Map download file name does not match title of web map item."
        )
        self.assertGreater(
            json_file_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_download_method_binary_data_outputpath(self):
        """
        When Item has binary data - like layer packages, ensure Item.download() downloads file
        into that path instead of returning None or binary stream.
        :return:
        """
        
        try:
            mmpk_item = self.gis.content.search("set1_mmpk *", "Mobile Map Package")[0]
        except IndexError as ie:
            mmpk_file = get_resource_path(
                relative_path="staging_data/item_class_test_data/set1_mmpk_usa.mmpk",
                verify=True,
                unique_copy=True,
            )

            mmpk_item = add_source_item(
                gis=self.gis,
                layer_name="set1_mmpk_usa",
                item_type=ItemTypeEnum.MOBILE_MAP_PACKAGE,
                source_data_path=mmpk_file,
                folder=self.item_test_folder,
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            map_pkg_file = mmpk_item.download(save_path=temp_dir)
            map_pkg_file_size = Path(map_pkg_file).stat().st_size

        self.assertIsInstance(
            map_pkg_file,
            str,
            "Calling download() on mmpk item does not return download str path",
        )
        self.assertEqual(
            str(Path(map_pkg_file).parent),
            temp_dir,
            "Download file location does not match known temporary directory.",
        )
        self.assertEqual(
            Path(map_pkg_file).suffix,
            ".mmpk",
            "Download file extension is not mmpk as expected"
        )
        self.assertEqual(
            Path(map_pkg_file).stem,
            mmpk_item.title,
            "Download file name does not match title of mmpk item."
        )
        self.assertGreater(
            map_pkg_file_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_get_data_method_Image(self):
        """
        For Image item, item.get_data(False) should return string representation of the item.
        :return:
        """
      
        try:
            img_item = self.gis.content.search(
                "set1_shifting_opportunity.png", "Image"
            )[0]
        except IndexError as ie:
            png_file = get_resource_path(
                relative_path="staging_data/item_class_test_data/set1_shifting_opportunity.png",
                verify=True,
                unique_copy=True,
            )
            img_item = add_source_item(
                gis=self.gis,
                layer_name="set1_shifting_opportunity",
                item_type=ItemTypeEnum.IMAGE,
                source_data_path=png_file,
                folder=self.item_test_folder,
            )
        with tempfile.TemporaryDirectory() as temp_dir:
            img_download_data = img_item.download()
            img_size = Path(img_download_data).stat().st_size

        self.assertIsInstance(
            img_download_data,
            str,
            "Calling download() on Image item does not return download str path",
        )
        self.assertTrue(
            Path(img_download_data).name.endswith(".png"),
            "Download file name does not match known input",
        )
        self.assertEqual(
            Path(img_download_data).stem,
            img_item.title,
            "Download file from Image item does not match known file name."
        )
        self.assertGreater(
            img_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_download_method_zero_size_data(self):
        """
        When Item has no data or 0kb size - ensure Item.download() returns None
        :return:
        """
        
        try:
            wmapp_item = self.gis.content.search(
                "set1_empty_webapp", "Web Mapping Application"
            )[0]
        except IndexError as ie:
            wmapp_item = self.item_test_folder.add(
                item_properties=ItemProperties(
                    title="set1_empty_webapp_api",
                    item_type=ItemTypeEnum.WEB_MAPPING_APPLICATION,
                    snippet="Test to create 0kb item from Python API",
                    tags=INTEGRATION_TEST_ITEM_TAG,
                )
            ).result()
        
        wmapp_download_file = wmapp_item.download()
        wmapp_download_file_size = Path(wmapp_download_file).stat().st_size
        
        self.assertIsNotNone(
            wmapp_download_file,
            "Calling download() on zero kb item returns None"
        )
        self.assertEqual(wmapp_download_file_size, 0, "Downloaded file size is not 0")

    def test_get_data_method_binary_data_tryjson_True(self):
        """
        When Item has binary data - like layer packages, word docs, ensure Item.get_data() downloads file
        into that path even if try_json is set to True
        :return:
        """
       
        try:
            word_item = self.gis.content.search("xsummary *", "Microsoft Word")[0]
        except IndexError as ie:
            word_file_path = get_resource_path(
                relative_path="staging_data/item_class_test_data/summary_temp.docx",
                verify=True,
                unique_copy=True,
            )
            word_item = add_source_item(
                gis=self.gis,
                layer_name="xsummary_temp",
                item_type=ItemTypeEnum.MICROSOFT_WORD,
                source_data_path=word_file_path,
                folder=self.item_test_folder
            )
        item_data = word_item.get_data(try_json=True)
        item_data_size = Path(item_data).stat().st_size

        self.assertIsInstance(
            item_data,
            str,
            "Calling get_data() on lpk item does not return download str path",
        )
        self.assertEqual(
            str(Path(item_data).parent),
            str(tempfile.gettempdir()),
            "Download file location does not match temporary directory."
        )
        self.assertTrue(
            Path(item_data).name.endswith(".docx"),
            "Download of Word item did not produce correct file extension."
        )
        self.assertGreater(
            item_data_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_get_data_method_binary_data_tryjson_False(self):
        """
        When Item has binary data - like layer packages, word docs, etc. ensure 
        Item.get_data() downloads file into a path when try_json is set to False.
        """
        try:
            word_item = self.gis.content.search("xsummary *", "Microsoft Word")[0]
        except IndexError as ie:
            word_file_path = get_resource_path(
                relative_path="staging_data/item_class_test_data/summary_temp.docx",
                verify=True,
                unique_copy=True,
            )
            word_item = add_source_item(
                gis=self.gis,
                layer_name="xsummary_temp",
                item_type=ItemTypeEnum.MICROSOFT_WORD,
                source_data_path=word_file_path,
                folder=self.item_test_folder,
            )
        item_data = word_item.get_data(try_json=False)
        item_data_size = Path(item_data).stat().st_size

        self.assertIsInstance(
            item_data,
            str,
            "Calling get_data() on map doc item does not return download str path",
        )
        self.assertEqual(
            str(Path(item_data).parent),
            str(tempfile.gettempdir()),
            "Download file location does not match temporary directory."
        )
        self.assertTrue(
            Path(item_data).name.endswith(".docx"),
            "Download of Word item did not produce correct file extension."
        )
        self.assertGreater(
            item_data_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_get_data_method_JSON_data_tryjson_False(self):
        """
        When Item has JSON data - like web maps, calling Item.get_data() with try_json False,
        should return the data as str instead of dict.
        :return:
        """

        webmap_item = self.chi_webmap
        if not webmap_item:
            unittest.skipTest("Web Map not published as part of setUpClass as expected.")

        item_data = webmap_item.get_data(try_json=False)

        self.assertIsInstance(
            item_data,
            str,
            "Calling get_data() on web map item does not return data as str with try_json is false",
        )
        self.assertTrue(
            "baseMapLayers" in item_data,
            "JSON string of web map does not have baseMapLayers as expected."
        )

    def test_get_data_method_JSON_data_tryjson_True(self):
        """
        When Item has JSON data - like web maps, calling Item.get_data() with try_json True,
        should return the data dict instead of str
        :return:
        """
        
        webmap_item = self.chi_webmap
        if not webmap_item:
            unittest.skipTest("Web Map not published as part of setUpClass as expected.")

        item_data = webmap_item.get_data(try_json=True)

        self.assertIsInstance(
            item_data,
            dict,
            "Calling get_data() on web map item does not return data as dict with try_json is true",
        )
        self.assertTrue(
            "baseMap" in list(item_data.keys()),
            "Web Map JSON does not contain a baseMap as required."
        )

    def test_get_data_method_zero_size_data_tryjson_False(self):
        """
        When Item has no data, calling Item.get_data() with try_json False,
        should return None.
        :return:
        """
        try:
            wmapp_item = self.gis.content.search(
                "set1_empty_webapp", "Web Mapping Application"
            )[0]
            wmapp_item.update({"tags":INTEGRATION_TEST_ITEM_TAG})
        except IndexError as ie:
            wmapp_item = self.item_test_folder.add(
                item_properties=ItemProperties(
                    title="set1_empty_webapp_api",
                    item_type=ItemTypeEnum.WEB_MAPPING_APPLICATION,
                    snippet="Test to create 0kb item from Python API",
                    tags=INTEGRATION_TEST_ITEM_TAG,
                )
            ).result()
        
        wmapp_data = wmapp_item.get_data(try_json=False)

        self.assertIsNone(
            wmapp_data,
            "Calling get_data() on empty item with tryjson False does not return None",
        )

    def test_get_data_method_zero_size_data_tryjson_True(self):
        """
        When Item has no data, calling Item.get_data() with try_json True,
        should return empty dict.
        :return:
        """
       
        try:
            wmapp_item = self.gis.content.search(
                "set1_empty *", "Web Mapping Application"
            )[0]
            wmapp_item.update({"tags":INTEGRATION_TEST_ITEM_TAG})
        except IndexError as ie:
            wmapp_item = self.item_test_folder.add(
                item_properties=ItemProperties(
                    title="set1_empty_webapp_api",
                    item_type=ItemTypeEnum.WEB_MAPPING_APPLICATION,
                    snippet="Test to create 0kb item from Python API",
                    tags=INTEGRATION_TEST_ITEM_TAG,
                )
            ).result()

        item_data = wmapp_item.get_data(try_json=True)

        self.assertEqual(
            len(item_data),
            0,
            "Calling get_data() on empty item with tryjson False does not return an empty dictionary.",
        )

    def test_get_data_method_empty_data_tryjson_True(self):
        """
        When Item has no data, but item.size > 0, calling Item.get_data() with try_json True,
        should return an empty dict.
        :return:
        """
        
        item = self.chicago_wfl_item
        if not item:
            self.skipTest("Feature Layer item not published as part of setUpClass as expected.")
        
        self.assertGreater(
            item.size,
            0,
            "Invalid item for this testcase, its size is not greater than 0",
        )

        item_data = item.get_data(try_json=True)

        self.assertEqual(
            len(item_data),
            0,
            "Calling get_data() on item with no data and tryjson False does not return empty dict.",
        )

    def test_overwrite_csv_item_source(self):
        """
        Update a csv item with new csv file. Ensure the contents are updated and
        itemid remains same.
        :return:
        """
        try:
            csv_item = [
                ci
                for ci in self.gis.content.search("set1_overwrite *", "CSV")
                if ci.title.endswith("old")
            ][0]
        except IndexError as ie:
            csv_path = get_resource_path(
                relative_path="staging_data/item_class_test_data/set1_overwrite_old.csv",
                verify=True,
                unique_copy=True
            )
        
            csv_item = add_source_item(
                gis=self.gis,
                layer_name="set1_overwrite_old",
                item_type=ItemTypeEnum.CSV,
                source_data_path=csv_path,
                folder=self.item_test_folder,
            )

        self.assertIsNotNone(csv_item, "CSV item not found and not added.")

        old_csv_data = csv_item.download()

        old_df = pd.read_csv(old_csv_data)
        self.assertEqual(len(old_df), 10, "Original csv file does not have 10 records.")
        old_item_id = csv_item.id

        # update csv item
        new_csv_path = get_resource_path(
            relative_path="staging_data/item_class_test_data/overwrite_data/set1_overwrite_new.csv",
            verify=True,
            unique_copy=True
        )
        new_item_id = csv_item.id

        self.assertEqual(
            old_item_id, new_item_id, "CSV item ID is not same after updating csv data."
        )

        item_update_result = csv_item.update({}, data=new_csv_path)

        self.assertTrue(
            item_update_result, "Calling update on csv item does not return True"
        )

        csv_download_path = csv_item.download()

        new_df = pd.read_csv(new_csv_path)
        downloaded_file_df = pd.read_csv(csv_download_path)
        self.assertEqual(
            new_df.shape,
            downloaded_file_df.shape,
            "The number of rows and columns in CSV item not updated with new csv data.",
        )

    def test_register_application(self):
        """tests the registering of an Application item"""
        
        for at in ["browser", "native", "server", "multiple"]:
            with self.subTest(f"Test for registering {at} app with api.", i=at):
                ip = ItemProperties(
                    title=f"{at}_app_register_api_test",
                    item_type=ItemTypeEnum.APPLICATION,
                    snippet="Test application for register method in api.",
                    tags=INTEGRATION_TEST_ITEM_TAG,
                )
                item = self.item_test_folder.add(
                    item_properties=ip
                ).result()
                reg = item.register(app_type=at)
                self.assertIsInstance(
                    item.app_info,
                    dict,
                    "The app_info property failed to return a dict."
                )
                self.assertGreater(
                    len(item.app_info),
                    0,
                    "the app_info property for registered app returns empty dict."
                )
                self.assertTrue(
                    reg.get("client_id", False),
                    f"Registering application {item.title} failed to generate client_id."
                )
                self.assertTrue(
                    reg.get("client_secret", False),
                    f"Registering application {item.title} failed to generate client_secret."
                )

    def test_unregister_application(self):
        """tests the unregistering of an Application item"""
        
        ip = ItemProperties(
            title=f"multiple_app_register_api_unreg_test",
            item_type=ItemTypeEnum.APPLICATION,
            snippet="Test application for register method in api.",
            tags=INTEGRATION_TEST_ITEM_TAG,
        )
        item = self.item_test_folder.add(
            item_properties=ip
        ).result()
        
        app_reg = item.register(app_type="multiple")

        unreg = item.unregister()

        self.assertTrue(
            unreg,
            "Unregistering an app field to return True."
        )
        self.assertEqual(
            len(item.app_info),
            0,
            "After unregistering an app the app_info property still returns dict with content."
        )

    def test_overwrite_manyHFS_using_csv_errors(self):
        """
        Multiple feature layers are published using the same csv. Updating the csv file and
        then attempting to overwrite should raise RunTime Error
        :return:
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
        Publish a feature layer with csv.
        Update the csv and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
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
        Publish a feature layer with file geodatabase.
        Update the fgdb and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
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
        Publish a feature layer with shape file
        Update the shp and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
      
        shp_flyr_items = [
            s 
            for s in self.gis.content.search("set1_Item_overwrite_HFS *", "Feature Layer")
            if s.title.endswith("shp")
        ]

        if shp_flyr_items:
            for shp_flyr_item in shp_flyr_items:
                shp_source_item = shp_flyr_item.related_items("Service2Data", "forward")[0]
                shp_source_item.delete(permanent=True)
                shp_flyr_item.delete(permanent=True)

        shp_source_file = get_resource_path(
            relative_path = "staging_data/item_class_test_data/set1_Item_overwrite_HFS_shp.zip",
            verify=True,
            unique_copy=True
        )
        shp_flyr_item = publish_test_item(
            gis=self.gis,
            item_type=ItemTypeEnum.SHAPEFILE,
            layer_name="set1_Item_overwrite_HFS_shp",
            source_data_path=shp_source_file,
            folder=self.item_test_folder,
        )
        shp_source_item = shp_flyr_item.related_items("Service2Data", "forward")[0]

        if not shp_flyr_item:
            self.skipTest("Feature Layer not published from shapefile.")

        orig_shp_flyr_item_id = shp_flyr_item.id
        orig_flayer = shp_flyr_item.layers[0]
        orig_fset = orig_flayer.query()
        orig_flayer_df = orig_fset.sdf

        orig_num_features = len(orig_flayer_df)

        # update shp item
        new_shp_path = get_resource_path(
            relative_path="staging_data/item_class_test_data/overwrite_data/set1_Item_overwrite_HFS_shp.zip",
            verify=True,
            unique_copy=True
        )

        item_update_result = shp_source_item.update({}, data=new_shp_path)
        self.assertTrue(
            item_update_result, 
            "Calling update on shp item does not return True"
        )

        try:
            overwrite_result = shp_source_item.publish(
                overwrite=True
            )
        except Exception as oe:
            print("Failed to overwrite Feature Layer with updated shapefile.")
            print(str(oe))
        
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
        Publish a feature layer with SD file
        Update the sd with another SD that is not marked for overwriting and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        
        sd_flyr_items = [
            sd
            for sd in self.gis.content.search("us_states_rivers *", "Feature Layer")
            if sd.title.endswith("_sd")
        ]
        if sd_flyr_items:
            for sd_flyr_item in sd_flyr_items:
                source_sd_item = sd_flyr_item.related_items("Service2Data", "forward")[0]
                source_sd_item.delete(permanent=True)
            sd_flyr_item.delete(permanent=True)

        source_sd_file = get_resource_path(
            relative_path="staging_data/item_class_test_data/us_states_rivers.sd",
            verify=True,
            unique_copy=True
        )
        sd_flyr_item = publish_test_item(
            gis=self.gis,
            layer_name="us_states_rivers_sd",
            item_type=ItemTypeEnum.SERVICE_DEFINITION,
            source_data_path=source_sd_file,
            folder=self.item_test_folder
        )
        source_sd_item = sd_flyr_item.related_items("Service2Data", "forward")[0]

        self.assertIsNotNone(
            sd_flyr_item,
            "Feature Layer not published from service defintion."
        )
        orig_fl_item_id = sd_flyr_item.id
        orig_num_layers = len(sd_flyr_item.layers)

        new_sd_path = get_resource_path(
            relative_path="staging_data/item_class_test_data/overwrite_data/us_states_rivers.sd",
            verify=True,
            unique_copy=True
        )
        item_update_result = source_sd_item.update({}, data=new_sd_path)
        self.assertTrue(
            item_update_result, "Calling update on sd item does not return True"
        )

        overwrite_result = source_sd_item.publish(overwrite=True)
        self.assertIsNotNone(
            overwrite_result, "Calling publish with overwrite True returns None"
        )
        new_wfl_item_id = overwrite_result.id

        self.assertEqual(
            orig_fl_item_id,
            new_wfl_item_id,
            "Item ID is not same after overwriting",
        )

        self.assertLess(
            len(overwrite_result.layers),
            orig_num_layers,
            "Number of rows needs to be more after overwriting",
        )

    def test_nonorg_public_Item_share_unshare_orggroup(self):
        """
        In AGOL, users can search for public items outside the org and share
        them to their group. This is a popular way to accumulate content in 
        their GIS.
        """
        public_data_item = self.gis.content.search(
            "title: Hurricane * AND access:public", 
            outside_org=True
        )[0]
        self.assertIsNotNone(
            public_data_item, "Cannot create an Item Obj using a non org public item id"
        )
        new_grp = self.gis.groups.create(
            title="aa_group_for_sharing_test",
            tags="ntgrtn-tst,new-member-default",
            description="Group created to test whether new user added",
            snippet="Group configured as New Member Default"
        )

        self.assertEqual(
            len(public_data_item.sharing.groups.list()), 
            0,
            "Public item should not be shared to any group by default."
        )

        self.assertEqual(
            len(new_grp.content()),
            0,
            "New group should not have any content by default."
        )

        public_data_item.sharing.groups.add(new_grp)

        import time
        time.sleep(50)

        self.assertIsNotNone(
            new_grp.content(),
            "New group should have content after adding public item to it."
        )
        new_grp_content = new_grp.content()

        time.sleep(50)

        interested_item = [
            i
            for i in new_grp_content
            if i.id == public_data_item.id
        ]
        self.assertEqual(
            len(interested_item), 
            1, 
            "Shared item not found in group's contents"
        )

        self.assertTrue(
            public_data_item.sharing.groups.remove(new_grp),
            "Unable to unshare public item with group"
        )

        self.assertTrue(
            new_grp.delete(),
            "Unable to delete group created for test."
        )

    def test_dependent_upon_ownItems(self):
        """
        As an item owner, I should be able to get my Item's dependencies
        :return:
        """

        # get an item
        chicago_csv_item = self.gis.content.search("title:Chicago_points", "CSV")[0]
        wm = self.gis.content.search("title:chicago_webmap *", "Web Map")[0]

        chicago_deps = chicago_csv_item.dependent_upon()
        wm_deps = wm.dependent_upon()

        # assert csv item dependency none
        self.assertIsNotNone(
            chicago_deps, "Unable to get dependencies for CSV item"
        )
        self.assertEqual(
            chicago_deps["total"],
            0,
            "A default CSV item should have 0 dependencies",
        )

        # assert webmap dependency
        self.assertIsNotNone(
            wm_deps, "Unable to get dependencies for a webmap item"
        )
        self.assertEqual(
            len(wm_deps["list"]),
            0,
            "dependent_upon method not supported with ArcGIS Online. Should return empty list.",
        )

if __name__ == "__main__":
    unittest.main()