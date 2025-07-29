# -------------------------------------------------------------------------------
# Name:        Item class tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
import os
import uuid
import tempfile
from pathlib import Path
import pandas as pd

from integration.config import (
    INTEGRATION_TEST_ITEM_TAG,
    get_resource_path,
    get_web_resource_path
)
from utils.decorators import integration_test, profiles
from utils.data_utils import (
    add_source_item,
    publish_test_item,
    cleanup_published_items,
    cleanup_folders
)

from arcgis.gis import ItemProperties, ItemTypeEnum, Item, GIS
from arcgis.layers import VectorTileLayer, Object3DLayer, MapFeatureLayer
from arcgis.features import FeatureLayer


#@profiles.admin_enterprise
@integration_test
class Test_Item_portal_builtin(unittest.TestCase):
    """
    Test to check if a Item object works with builtin portal
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """
        # Enterprise 11.5
        cls.gis = GIS(
            url="https://rextapilnx02eb.esri.com/portal",
            username="PAPIadmin",
            password="PAPIletmein01",
            profile="your_enterprise12_admin_profile"
        )
        
        # Enterprise 12.0
        #cls.gis = GIS(
            #url="https://dev0016752.esri.com/portal",
            #username="admin",
            #password="esri.agp",
            #verify_cert=False
        #)

        cls.item_test_folder = cls.gis.content.folders._get_or_create(
            "aa_ntgrtn_tst_gis_item_class"
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
            cls.set1_overwrite_HFS_csv2 = [
                i 
                for i in cls.gis.content.search(
                    "set1_overwrite_HFS_csv2", "Feature Layer"
                ) if i.title.endswith("csv2")
            ][0]
            cls.csv2_source_csv_item = cls.set1_overwrite_HFS_csv2.related_items("Service2Data", "forward")[0]
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
                prep_for_editing=False,
                folder=cls.item_test_folder
            )
            cls.csv2_source_csv_item = cls.set1_overwrite_HFS_csv2.related_items("Service2Data", "forward")[0]

        try:
            cls.flyr_from_fgdb_item = cls.gis.content.search(
                "set1_HFS_fgdb_gdb", "Feature Layer"
            )[0]
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
                source_data_path=cls.fgdb_source_path,
                folder=cls.item_test_folder,
            )
            cls.fgdb_source_item = cls.flyr_from_fgdb_item.related_items(
                "Service2Data", "forward"
            )[0]

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
            if "Item already exists in target folder" in str(me):
                pass
            
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
        vtpk_package_file = get_web_resource_path(
            relative_path="data/set2_vtpk_worldgreen.vtpk", 
            unique_copy=True
        )
        
        vtl_pkg_item = self.item_test_folder.add(
            item_properties=ItemProperties(
                title="set2_vtpk_worldgreen",
                item_type=ItemTypeEnum.VECTOR_TILE_PACKAGE,
                snippet="Vector tile package item added with api.",
                description="Vector tile package item added to folders for API integration tests.",
                tags=INTEGRATION_TEST_ITEM_TAG, 
            ),
            file=vtpk_package_file
        ).result()
        
        vtl_item = vtl_pkg_item.publish()

        self.assertIsNotNone(vtl_item, "Publish of VTPK item failed.")
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

    def test_publish_spk(self):
        if self.gis.version >= [2024, 2] and self.gis.properties.isPortal:
            srv_mgr = self.gis.admin.servers
            host_srv = srv_mgr.get(role="HOSTING_SERVER")[0]
            dstores = [
                d
                for d in host_srv.datastores.list()
                if d.properties.type == "objectStore"
            ]
            if not dstores:
                self.skipTest(
                    "Hosted scene layers cannot be published on this Enterprise release unless an Object Store is configured."
                )

        prev_scn_item = [
            sc for sc in self.gis.content.search(
                query="set2_spk *", item_type=ItemTypeEnum.SCENE_SERVICE.value
            ) if sc.title.endswith("SD3dbuildings")
        ]
        if prev_scn_item:
            for scn_item in prev_scn_item:
                scn_pkg = scn_item.related_items("Service2Data", "forward")[0]
                scn_pkg.delete(permanent=True)
            scn_item.delete(permanent=True)
        
        spk_package_file = get_web_resource_path(
            relative_path="data/set2_spk_SD3dbuildings.spk",
            unique_copy=True
        )

        scn_pkg_item = self.item_test_folder.add(
            item_properties=ItemProperties(
                title="set2_spk_SD3dbuildings",
                item_type=ItemTypeEnum.SCENE_PACKAGE,
                snippet="Publish Scene Service from Service Definition Package.",
                description="Test item published with api.",
                tags=["ntgrtn-tst"]
            ),
            file=spk_package_file
        ).result()
        scn_item = scn_pkg_item.publish()

        self.assertTrue(scn_item, f"Failed to publish Scene Service.")
        self.assertIsInstance(
            scn_item, Item, "Failed to publish {scn_item.title} Scene Service."
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

    def test_publish_tpk(self):
        prev_tlyr_item = [
            tlyr for tlyr in self.gis.content.search(
                query="set3_tpk *", item_type=ItemTypeEnum.MAP_SERVICE.value
            ) if tlyr.title.endswith("_SD")
        ]
        if prev_tlyr_item:
            for tlyr_item in prev_tlyr_item:
                try:
                    tlyr_item.related_items("Service2Data", "forward")[0].delete(permanent=True)
                    tlyr_item.delete(permanent=True)
                except IndexError:
                    self.skipTest("Failed to delete previously published tile layer item.")
              
        tpk_package_file = get_web_resource_path(
            relative_path="data/set3_tpk_SD.tpk",
            unique_copy=True
        )

        tile_lyr_item = publish_test_item(
            gis=self.gis,
            layer_name="set3_tpk_SD",
            item_type=ItemTypeEnum.TILE_PACKAGE,
            source_data_path=tpk_package_file,
            prep_for_editing=False,
            folder=self.item_test_folder,
        )

        self.assertTrue(
            tile_lyr_item, f"Failed to publish set3_tpk_SD Map Service."
        )
        self.assertIsInstance(
            tile_lyr_item,
            Item,
            f"Failed to publish {tile_lyr_item.title} Tile Layer item.",
        )
        self.assertEqual(
            tile_lyr_item.title,
            "set3_tpk_SD",
            "Title of published item does not match service_title argument.",
        )
        self.assertEqual(
            tile_lyr_item.type,
            ItemTypeEnum.MAP_SERVICE.value,
            f"{tile_lyr_item.title} is not a Map Service item.",
        )
        self.assertGreaterEqual(
            len(tile_lyr_item.layers),
            1,
            f"Failed to publish layer(s) for {tile_lyr_item.title} Tile Layer.",
        )
        self.assertIsInstance(
            tile_lyr_item.layers[0],
            MapFeatureLayer,
            f"{tile_lyr_item.title} layer is not a MapFeatureLayer as expected.",
        )

    def test_publish_shp(self):
        shp_source_data_t = get_resource_path(
            relative_path="staging_data/USA_Major_Cities.zip", 
            verify=True,
            unique_copy=True
        )
        shp_based_item = publish_test_item(
            gis=self.gis,
            layer_name="usa_major_cities_itemtest",
            item_type=ItemTypeEnum.SHAPEFILE,
            source_data_path=shp_source_data_t,
            prep_for_editing=False,
            folder=self.item_test_folder,
        )
        rel_item = shp_based_item.related_items("Service2Data", "forward")[0]

        self.assertIsInstance(
            shp_based_item, Item, "Publish failed to result in an Item."
        )
        self.assertEqual(
            rel_item.type,
            ItemTypeEnum.SHAPEFILE.value,
            "Source item not a shapefile as expected.",
        )
        self.assertEqual(
            shp_based_item.type,
            ItemTypeEnum.FEATURE_SERVICE.value,
            "Failed to publish feature service from shapefile.",
        )
        self.assertEqual(
            shp_based_item.title,
            "usa_major_cities_itemtest",
            "Failed to publish item with layer_name argument.",
        )
        self.assertGreater(
            len(shp_based_item.layers),
            0,
            "Publish failed to publish service with at least 1 layer.",
        )
        self.assertIsInstance(
            shp_based_item.layers[0],
            FeatureLayer,
            "Publish failed to create feature layers for service.",
        )
        self.assertTrue(shp_based_item.layers[0].query())
        self.assertGreater(
            shp_based_item.layers[0].query(return_count_only=True),
            0,
            "Features failed to publish for feature layer in service.",
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
  
    def test_download_method_empty_data(self):
        """
        When Item has no data, Item.download() should download to a file of size 0
        :return:
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            chicago_data = self.chicago_wfl_item.download(save_path=temp_dir)
            chicago_data_size = os.stat(chicago_data).st_size

        self.assertIsNotNone(
            chicago_data,
            "Calling download() on Item with empty resource throws error",
        )
        self.assertEqual(chicago_data_size, 0, "File size of empty item is > 0")

    def test_download_method_empty_data_nopath(self):
        """
        When Item has no data, Item.download() should download to a file of size 0
        :return:
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            chicago_data = self.chicago_wfl_item.download()
            chicago_data_size = os.stat(chicago_data).st_size

        self.assertIsNotNone(
            chicago_data,
            "Calling download() on Item with empty resource throws error",
        )
        self.assertEqual(chicago_data_size, 0, "File size of empty item is > 0")
  
    def test_download_method_txt_data_nopath(self):
        """
        When no path is provided, Item.download() downloads to sys temp dir
        :return:
        """
        chicago_csv_item = self.chicago_wfl_item.related_items(
            "Service2Data", "forward"
        )[0]
        with tempfile.TemporaryDirectory() as temp_dir:
            chicago_dload = chicago_csv_item.download()
            chicago_data = Path(chicago_dload)
            chicago_data_size = chicago_data.stat().st_size

        self.assertIsInstance(
            chicago_dload,
            str,
            "Item download() for csv item does not return path as a string."
        )

        self.assertIsInstance(
            chicago_data,
            Path,
            "Setting item download() to a path object failed.",
        )
        self.assertTrue(
            chicago_data.name.startswith("Chicago_points_"),
            "Download file name does not match expected name.",
        )
        self.assertEqual(
            chicago_data.suffix,
            ".csv",
            "Downloaded file is not a csv file as expected.",
        )
        self.assertGreater(
            chicago_data_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_download_method_txt_data_outputpath(self):
        """
        When given a download path, ensure Item.download() downloads file into that path
        :return:
        """
        chicago_csv_item = self.chicago_wfl_item.related_items(
            "Service2Data", "forward"
        )[0]
        with tempfile.TemporaryDirectory() as temp_dir:
            chicago_dload = chicago_csv_item.download(save_path=temp_dir)
            chicago_data = Path(chicago_dload)
            chicago_data_size = chicago_data.stat().st_size

        self.assertIsInstance(
            chicago_data,
            Path,
            "Download of csv item does not return path as expected.",
        )
        self.assertTrue(
            str(chicago_data).startswith(str(temp_dir)),
            "Download file name does not match known input",
        )
        self.assertEqual(
            chicago_data.suffix,
            ".csv",
            "Downloaded file is not a csv file as expected.",
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
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = JSON_item.download(save_path=temp_dir)
            json_file_size = os.stat(json_file).st_size

        self.assertIsInstance(
            json_file,
            str,
            "Calling download() on webmap item does not return download str path",
        )
        self.assertTrue(
            json_file.startswith(str(temp_dir)),
            "Download file name does not match known input",
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
            JSON_item = self.gis.content.search("set1_mmpk_usa", "Mobile Map Package")[
                0
            ]
        except IndexError as ie:
            mmpk_file = get_resource_path(
                relative_path="staging_data/item_class_test_data/set1_mmpk_usa.mmpk",
                verify=True,
                unique_copy=True,
            )

            JSON_item = add_source_item(
                gis=self.gis,
                layer_name="set1_mpk_usa",
                item_type=ItemTypeEnum.MOBILE_MAP_PACKAGE,
                source_data_path=mmpk_file,
                folder=self.item_test_folder,
            )
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = JSON_item.download(save_path=temp_dir)
            json_file_size = os.stat(json_file).st_size

        self.assertIsInstance(
            json_file,
            str,
            "Calling download() on mmpk item does not return download str path.",
        )
        self.assertTrue(
            json_file.startswith(str(temp_dir)),
            "Download file name does not match known input.",
        )
        self.assertGreater(
            json_file_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_get_data_method_Image(self):
        """
        For Image item, item.get_data(False) should return string representation of the item.
        :return:
        """
        try:
            data_item = self.gis.content.search(
                "set1_shifting_opportunity.png", "Image"
            )[0]
        except IndexError as ie:
            png_file = get_resource_path(
                relative_path="staging_data/item_class_test_data/set1_shifting_opportunity.png",
                verify=True,
                unique_copy=True,
            )
            data_item = add_source_item(
                gis=self.gis,
                layer_name="set1_shifting_opportunity",
                item_type=ItemTypeEnum.IMAGE,
                source_data_path=png_file,
                folder=self.item_test_folder,
            )
        with tempfile.TemporaryDirectory() as temp_dir:
            item_data = data_item.download()
            data_size = os.stat(item_data).st_size

        self.assertIsInstance(
            item_data,
            str,
            "Calling download() on Image item does not return download str path",
        )
        self.assertTrue(
            item_data.endswith(".png"),
            "Download file name does not match known input",
        )
        self.assertGreater(data_size, 0, "Downloaded file size is not greater than 0")
  
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
        json_file = wmapp_item.download()
        json_file_size = os.stat(json_file).st_size

        self.assertIsNotNone(
            json_file, "Calling download() on zero kb item returns None"
        )
        self.assertEqual(json_file_size, 0, "Downloaded file size is not 0")
   
    def test_get_data_method_binary_data_tryjson_True(self):
        """
        When Item has binary data - like layer packages, word docs, ensure Item.get_data() downloads file
        into that path even if try_json is set to True
        :return:
        """
        try:
            item = self.gis.content.search("set1_lpk", "Layer Package")[0]
        except IndexError as ie:
            lpk_source_data = get_resource_path(
                relative_path="staging_data/item_class_test_data/set1_lpk.lpk"
            )
            item = self.item_test_folder.add(
                item_properties=ItemProperties(
                    title="set1_lpk",
                    item_type=ItemTypeEnum.LAYER_PACKAGE,
                    snippet="Layer Package to test binary download",
                    tags=[INTEGRATION_TEST_ITEM_TAG],
                ),
                file=lpk_source_data,
            ).result()

        item_data = item.get_data(try_json=True)
        item_data_size = os.stat(item_data).st_size

        self.assertIsInstance(
            item_data,
            str,
            "Calling get_data() on lpk item does not return download str path",
        )
        self.assertTrue(
            item_data.startswith(str(tempfile.gettempdir())),
            "Download file name does not match known input",
        )
        self.assertGreater(
            item_data_size, 0, "Downloaded file size is not greater than 0."
        )
    
    def test_get_data_method_binary_data_tryjson_False(self):
        """
        When Item has binary data - like layer packages, word docs, ensure Item.get_data() downloads file
        into that path when try_json is set to False
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
        item_data = word_item.get_data(try_json=False)
        item_data_size = Path.stat(item_data).st_size

        self.assertIsInstance(
            item_data,
            str,
            "Calling get_data() on map doc item does not return download str path",
        )
        self.assertTrue(
            item_data.startswith(str(tempfile.gettempdir())),
            "Download file name does not match known input",
        )
        self.assertGreater(
            item_data_size, 0, "Downloaded file size is not greater than 0"
        )

    def test_get_data_method_JSON_data_tryjson_False(self):
        """
        When Item has JSON data - like web maps, calling Item.get_data() with try_json False,
        should return the data as str instead of dict
        :return:
        """

        item = self.chi_webmap
        item_data = item.get_data(try_json=False)

        self.assertIsInstance(
            item_data,
            str,
            "Calling get_data() on web map item does not return data as str with try_json equal false",
        )
        self.assertTrue(
            "baseMapLayers" in item_data,
            "JSON from web map item does not have baseMapLayers as expcted."
        )
   
    def test_get_data_method_JSON_data_tryjson_True(self):
        """
        When Item has JSON data - like web maps, calling Item.get_data() with try_json True,
        should return the data dict instead of str
        :return:
        """
        item = self.chi_webmap
        item_data = item.get_data(try_json=True)

        self.assertIsInstance(
            item_data,
            dict,
            "Calling get_data() on web map item does not return data as dict with try_json True",
        )

    def test_get_data_method_zero_size_data_tryjson_False(self):
        """
        When Item has a 0kb Size, as in creating a Web Application with no file
        data_url, or text argument, calling Item.get_data() with try_json False
        should return None.
        """
        try:
            item = self.gis.content.search(
                "set1_empty_webapp", "Web Mapping Application"
            )[0]
        except IndexError as ie:
            item = self.item_test_folder.add(
                item_properties=ItemProperties(
                    title="set1_empty_webapp_api",
                    item_type=ItemTypeEnum.WEB_MAPPING_APPLICATION,
                    snippet="Test to create 0kb item from Python API",
                    tags=INTEGRATION_TEST_ITEM_TAG,
                )
            ).result()
        item_data = item.get_data(try_json=False)

        self.assertIsNone(
            item_data,
            "Calling get_data() on empty item with tryjson False does not return None",
        )
   
    def test_get_data_method_zero_size_data_tryjson_True(self):
        """
        When Item has a 0kb Size, as in creating a Web Application with no
        file, data_url, or text argument, calling Item.get_data() with try_json
        True should return an empty dictionary.
        :return:
        """
        try:
            item = self.gis.content.search(
                "set1_empty_webapp", "Web Mapping Application"
            )[0]
        except IndexError as ie:
            item = self.item_test_folder.add(
                item_properties=ItemProperties(
                    title="set1_empty_webapp_api",
                    item_type=ItemTypeEnum.WEB_MAPPING_APPLICATION,
                    snippet="Test to create 0kb item from Python API",
                    tags=INTEGRATION_TEST_ITEM_TAG,
                )
            ).result()
        item_data = item.get_data(try_json=True)

        self.assertIsInstance(
            item_data,
            dict,
            "Calling get_data() on feature layer item does not return empty dictionary.",
        )
        self.assertEqual(
            len(item_data),
            0,
            "Calling get_data() on empty item with tryjson False does not return empty dictionary.",
        )
  
    def test_get_data_method_empty_data_tryjson_True(self):
        """
        When Item has no data at data endpoint, such as with Featiure Layer
        items but item.size is greater than 0, calling Item.get_data() with
        try_json True should return an empty dictinary.
        """
        try:
            item = self.gis.content.search("set1_Chicago", "Feature Layer")[0]
        except IndexError as ie:
            item = self.chicago_wfl_item
        self.assertGreater(
            item.size,
            0,
            "Invalid item for this testcase, its size is not greater than 0",
        )

        item_data = item.get_data(try_json=True)

        self.assertIsInstance(
            item_data,
            dict,
            "Calling get_data() on feature layer item does not return empty dictionary.",
        )
        self.assertEqual(
            len(item_data),
            0,
            "Calling get_data() on feature layer item with try_json True does not return empty dictionary.",
        )

    def test_overwrite_csv_item(self):
        """
        Update a csv item with new csv file. Ensure the contents are updated and
        itemid remains same.
        """

        try:
            csv_item = self.gis.content.search("set1_overwrite_old", "CSV")[0]
        except IndexError as ie:
            csv_source_file = get_resource_path(
                relative_path="staging_data/item_class_test_data/set1_overwrite_old.csv",
                verify=True,
                unique_copy=True
            )
            csv_item = add_source_item(
                gis=self.gis,
                layer_name="set1_overwrite_old",
                item_type=ItemTypeEnum.CSV,
                source_data_path=csv_source_file,
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
        item_update_result = csv_item.update({}, data=new_csv_path)
        self.assertTrue(
            item_update_result, "Calling update on csv item does not return True"
        )
        new_item_id = csv_item.id

        self.assertEqual(
            old_item_id, new_item_id, "Item ID is not same after overwriting"
        )

        # verify content is updated
        csv_download_path = csv_item.download()

        # read contents
        new_df = pd.read_csv(new_csv_path)
        downloaded_file_df = pd.read_csv(csv_download_path)
        self.assertEqual(
            new_df.shape,
            downloaded_file_df.shape,
            "The number of rows and columns in CSV item not updated with new csv data.",
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
 
    def test_overwrite_HFS_using_csv2(self):
        """
        Update a CSV item serving as a source for a Feature Layer item and
        ensure csv content are updated. Overwrite the Feature Layer item
        using the updated csv contents and ensure contents.
        """

        # update csv item
        new_csv_path = get_resource_path(
            relative_path="staging_data/item_class_test_data/overwrite_data/set1_overwrite_HFS_csv2.csv",
            verify=True,
            unique_copy=True
        )

        before_csv = self.csv2_source_csv_item.download()
        before_df = pd.read_csv(before_csv)
        before_count = len(before_df)
        before_feature_count = self.set1_overwrite_HFS_csv2.layers[0].query(
            return_count_only=True
        )

        item_update_result = self.csv2_source_csv_item.update({}, data=new_csv_path)
        self.assertTrue(
            item_update_result, "Calling update on csv item does not return True"
        )
        after_csv = self.csv2_source_csv_item.download()
        after_df = pd.read_csv(after_csv)
        after_count = len(after_df)

        self.assertGreater(
            after_count, before_count, "CSV item id not update with new data."
        )

        # overwrite the feature layer
        overwrite_flyr_item = self.csv2_source_csv_item.publish(overwrite=True)
        self.assertIsNotNone(overwrite_flyr_item, "Publish with new data failed.")
        after_feature_count = overwrite_flyr_item.layers[0].query(
            return_count_only=True
        )
        self.assertNotEqual(
            before_feature_count,
            after_feature_count,
            "Publish did not properly use data from overwrite.",
        )

    def test_overwrite_HFS_using_fgdb(self):
        """
        Publish a feature layer with file geodatabase.
        Update the fgdb and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region find wfl is present, else publish it.
        wfl_item = self.flyr_from_fgdb_item
        fgdb_item = self.fgdb_source_item

        if wfl_item is None:
            print("File Geodatabase item did not publish in setUpClass.")

        # delete all features from the feature layer
        flayer = wfl_item.layers[0]
        delete_result = flayer.delete_features(where="1=1")
        num_features_after_delete = flayer.query(return_count_only=True)
        self.assertEqual(
            num_features_after_delete, 0, "Delete_features did not remove all features."
        )

        try:
            new_fgdb_path = get_resource_path(
                relative_path="staging_data/item_class_test_data/overwrite_data/set1_Item_overwrite_HFS_fgdb.gdb.zip",
                verify=True,
                unique_copy=True
            )
            item_update_result = fgdb_item.update({}, data=new_fgdb_path)
            self.assertTrue(
                item_update_result, "Calling update on fgdb item does not return True"
            )

            # overwrite the feature layer
            overwrite_result = fgdb_item.publish(overwrite=True)
            self.assertIsNotNone(
                overwrite_result, "Calling publish with overwrite True returns None"
            )
            new_wfl_item_id = overwrite_result.id

            self.assertEqual(
                wfl_item.id, new_wfl_item_id, "Item ID is not same after overwriting"
            )

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(
                num_features_after_overwrite, 0, "Overwrite failed to add new features."
            )

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    def test_dependent_upon_ownItems(self):
        """
        As an item owner, I should be able to get my Item's dependencies
        """
        chicago_csv_item = self.chicago_wfl_item.related_items(
            "Service2Data", "forward"
        )[0]
        wm = self.chi_webmap
        try:
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
            self.assertGreaterEqual(
                len(wm_deps["list"]),
                2,
                "Dependencies not found for Chicago Web Map.",
            )
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

if __name__ == "__main__":
    unittest.main()