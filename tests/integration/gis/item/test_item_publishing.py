# -------------------------------------------------------------------------------
# Name:        Test for the publish method of the Item class. Multiple file types
#              are published and output properties confirmed.
# Purpose:     Integration tests for publishing items with the ArcGIS Python API.
# -------------------------------------------------------------------------------

import unittest
import time

from integration.config import (
    get_resource_path,
    get_web_resource_path,
    INTEGRATION_TEST_ITEM_TAG,
)
from utils.decorators import integration_test, profiles
from utils.data_utils import cleanup_published_items, cleanup_folders

from arcgis.gis import ItemProperties, ItemTypeEnum, Item
from arcgis.features import FeatureLayer
from arcgis.layers import VectorTileLayer, Object3DLayer


def setUpModule():
    import warnings

    warnings.filterwarnings("ignore")


@profiles.admin_agol
@integration_test
class Test_Item_publish_file_types(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Test for publishing different file types to deployment.
        """
        print(f"{'=' * 5} begin setUp {cls.__name__}")
        # Get or create a folder to store items created during test run
        cls.item_test_publish_folder = cls.gis.content.folders._get_or_create(
            "item_publish_ntgrtn_tests"
        )
        print(f"{'=' * 5} end setup {'=' * 30}\n")

    @classmethod
    def tearDownClass(cls):
        print(f"\n{'=' * 5} begin teardownClass: {cls.__name__}")
        test_items = list(cls.item_test_publish_folder.list())
        if test_items:
            cleanup_published_items(test_items)
        else:
            print(f"Test items already cleared from test folder.")
        cleanup_folders(gis=cls.gis, folder_names=[cls.item_test_publish_folder.name])
        print(f"{'=' * 5} end tearDownClass {'=' * 10}\n")

    def setUp(self):
        print(f"\n{'-' * 40}\nTest: starting {self._testMethodName}...")
        self._start_time = time.time()

    def tearDown(self):
        elapsed_time = time.time() - self._start_time
        print(f"{' ' * 4}...test took {elapsed_time/60:.2f} minutes.\n")
    @unittest.skip("for now")
    def test_publish_csv(self):
        csv_source_file = get_resource_path(
            relative_path="staging_data/item_class_test_data/RUS_cities.csv",
            verify=True,
            unique_copy=True,
        )

        csv_file_item = self.item_test_publish_folder.add(
            item_properties=ItemProperties(
                title="Russian_cities",
                item_type=ItemTypeEnum.CSV,
                snippet="CSV item published with Folder in API.",
                description="CSV item added for Python API publish integration tests.",
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=csv_source_file,
        ).result()
        csv_lyr_item = csv_file_item.publish(
            publish_parameters={"name": "Russian_cities_api"}
        )
        self.assertEqual(
            csv_file_item.type,
            "CSV",
            "CSV item added with folder returns incorrect value for type property.",
        )
        self.assertIsInstance(
            csv_lyr_item, Item, "Failed to publish CSV item as a featur layer Item."
        )
        self.assertEqual(
            csv_lyr_item.type,
            "Feature Service",
            "Publishing zipped file geodatabase does not create a feature service.",
        )
        self.assertEqual(
            len(csv_lyr_item.layers),
            1,
            "No feature layers found in published feature service.",
        )
        self.assertIsInstance(
            csv_lyr_item.layers[0],
            FeatureLayer,
            "Feature Layer item layers property not returning a FeatureLayer object.",
        )
        self.assertGreater(
            len(csv_lyr_item.layers[0].query().features),
            0,
            "No features found in published feature service.",
        )
    @unittest.skip("for now")
    def test_publish_fgdb(self):
        cities_fgdb_source = get_resource_path(
            relative_path="staging_data/item_class_test_data/set2_USAcities.zip",
            verify=True,
            unique_copy=True,
        )

        cities_fgdb_item = self.item_test_publish_folder.add(
            item_properties=ItemProperties(
                title="set2_USAcities",
                item_type=ItemTypeEnum.FILE_GEODATABASE,
                snippet="File geodatabase item added in Folder with API.",
                description="File geodatabase item for Python API item integration tests.",
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=cities_fgdb_source,
        ).result()
        cities_lyr_item = cities_fgdb_item.publish(
            publish_parameters={"name": "set2_USAcities_api"}
        )

        self.assertEqual(
            cities_fgdb_item.type,
            "File Geodatabase",
            "Item added with folder not a file geodatabase item as expected",
        )
        self.assertIsInstance(
            cities_lyr_item,
            Item,
            "Failed to publish Item from zipped file geodatabase.",
        )
        self.assertEqual(
            cities_lyr_item.type,
            "Feature Service",
            "Publishing zipped file geodatabase does not create a feature service.",
        )
        self.assertEqual(
            len(cities_lyr_item.layers),
            1,
            "No feature layers found in published feature service.",
        )
        self.assertIsInstance(
            cities_lyr_item.layers[0],
            FeatureLayer,
            "Feature Layer item layers property not returning a FeatureLayer object.",
        )
        self.assertGreater(
            len(cities_lyr_item.layers[0].query().features),
            0,
            "No features found in published feature service.",
        )
    @unittest.skip("for now")
    def test_publish_vtpk(self):
        vtpk_package_file = get_web_resource_path(
            relative_path="set2_vtpk_worldgreen.vtpk",
            unique_copy=True,
        )

        vtl_pkg_item = self.item_test_publish_folder.add(
            item_properties=ItemProperties(
                title="set2_vtpk_worldgreen",
                item_type=ItemTypeEnum.VECTOR_TILE_PACKAGE,
                snippet="Vector tile package added with Folder in Python API.",
                description="Vector tile pacakge for Python API integration testing.",
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=vtpk_package_file,
        ).result()
        vtl_item = vtl_pkg_item.publish(
            publish_parameters={"name": "set2_vtpk_worldgreen_api"}
        )

        self.assertEqual(
            vtl_pkg_item.type,
            "Vector Tile Package",
            "Data item for vector tile item is not vector tile package as expected.",
        )
        self.assertIsNotNone(
            vtl_item, "Publish of vectory tile layer from VTPK item failed."
        )
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
    @unittest.skip("for now")
    def test_publish_spk(self):
        if self.gis._is_kubernetes:
            self.skipTest("Scene package format spk not supported on Kubernetes.")
        spk_package_file = get_web_resource_path(
            relative_path="set2_spk_SD3dbuildings.spk", unique_copy=True
        )
        scn_pkg_item = self.item_test_publish_folder.add(
            item_properties=ItemProperties(
                title="set2_spk_SD3dbuildings",
                item_type=ItemTypeEnum.SCENE_PACKAGE,
                snippet="Scene package added with Folder in Python API.",
                description="Scene package for Python API integration testing.",
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=spk_package_file,
        ).result()
        scn_item = scn_pkg_item.publish(
            publish_parameters={"name": "set2_spk_SD3dbuidings_api"}
        )

        self.assertEqual(
            scn_pkg_item.type,
            "Scene Package",
            "Scene package item does not return correct value for type property.",
        )
        self.assertTrue(
            scn_item,
            f"Failed to publish Scene Service from {scn_pkg_item.title} {scn_pkg_item.type}.",
        )
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
    @unittest.skip("for now")
    def test_publish_slpk(self):
        if self.gis.version >= [2024, 2]:
            if self.gis.properties.isPortal and not self.gis._is_kubernetes:
                srv_mgr = self.gis.admin.servers
                host_srv = srv_mgr.get(role="HOSTING_SERVER")[0]
                dstores = [
                    d
                    for d in host_srv.datastores.list()
                    if d.properties.type == "objectStore"
                ]
                if not dstores:
                    self.skipTest(
                        "Hosted scene layers require an Object Store for publication."
                    )
            elif self.gis._is_kubernetes:
                dstores = self.gis.admin.datastores
                dstore_types = [d.type for d in dstores.stores]
                if not "objectStore" in dstore_types:
                    self.skipTest(
                        "Hosted scene layers require an Object Store for publication."
                    )

        slpk_package_file = get_web_resource_path(
            relative_path="set2_slpk_Vancouver.slpk", unique_copy=True
        )

        scn_pkg_item = self.item_test_publish_folder.add(
            item_properties=ItemProperties(
                title="set2_slpk_Vancouver",
                item_type=ItemTypeEnum.SCENE_PACKAGE,
                snippet="Scene layer published from API integration test.",
                description="Vancouver scene published from slpk source file.",
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=slpk_package_file,
        ).result()

        scn_item = scn_pkg_item.publish(
            publish_parameters={"name": "set2_slpk_Vancouver_api"}
        )

        self.assertEqual(
            scn_pkg_item.type,
            "Scene Package",
            "Scene item related data item is not a scene package as expected.",
        )
        self.assertTrue(
            scn_item,
            f"Failed to publish Scene Service from {scn_pkg_item.title} {scn_pkg_item.type}.",
        )
        self.assertIsInstance(
            scn_item, Item, f"Failed to publish {scn_pkg_item.title} Scene package."
        )
        self.assertEqual(
            scn_item.type,
            ItemTypeEnum.SCENE_SERVICE.value,
            f"{scn_item.title} is not a Scene Service item.",
        )

        # added to allow for layer publish to complete
        time.sleep(60)
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
        if self.gis._is_kubernetes:
            self.skipTest("Tile package format tpk not supported on Kubernetes.")
        tile_pkg_file = get_web_resource_path(
            relative_path="set3_tpk_SD.tpk", unique_copy=True
        )

        tile_pkg_item = self.item_test_publish_folder.add(
            item_properties=ItemProperties(
                title="set3_tpk_SD",
                item_type=ItemTypeEnum.TILE_PACKAGE,
                snippet="Tile package item added with Folder in Python API.",
                description="Tile package item for Python API integration teting",
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=tile_pkg_file,
        ).result()
        tile_lyr_item = tile_pkg_item.publish(
            publish_parameters={
                "name": "set3_tpk_SD_api"
            }
        )
        self.assertEqual(
            tile_pkg_item.type,
            "Tile Package",
            "Tile layer item data item is not a tile package as expected.",
        )
        self.assertTrue(tile_lyr_item, "Failed to publish tile layer from TPK item.")
        self.assertIsInstance(
            tile_lyr_item,
            Item,
            f"Publishing tpk item does not return an Item {tile_lyr_item.title}.",
        )
        self.assertEqual(
            tile_lyr_item.type,
            "Map Service",
            "Publishing TPK does not create an Map Service item.",
        )
        self.assertTrue(
            len(tile_lyr_item.layers) > 0, "No layers published in Map Service."
        )

    def test_publish_tpkx(self):
        tpkx_package_file = get_web_resource_path(
            relative_path="redlands_testcase22.tpkx", unique_copy=True
        )

        tilex_pkg_item = self.item_test_publish_folder.add(
            item_properties=ItemProperties(
                title="Redlands_tiles",
                item_type=ItemTypeEnum.TILE_PACKAGE,
                snippet="Tpkx file added with Folder in API.",
                description="Tile package x format for Python API integration tests.",
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=tpkx_package_file,
        ).result()

        tilex_lyr_item = tilex_pkg_item.publish(
            publish_parameters={
                "name": "redlands_testcase_tpkx_api"
            }
        )

        self.assertEqual(
            tilex_pkg_item.type,
            "Tile Package",
            "Related data item to Map Service is not tile package.",
        )
        self.assertIsNotNone(
            tilex_lyr_item, "Failed to find tile layer or publish TPKX item."
        )

        self.assertIsInstance(tilex_lyr_item, Item, "Tile layer is not an item.")

        self.assertEqual(
            tilex_lyr_item.type,
            "Map Service",
            "Publishing TPKX does not create Map Service item.",
        )
        self.assertGreater(
            len(tilex_lyr_item.layers),
            0,
            "Tile layer does not have layers as expected.",
        )
    @unittest.skip("for now")
    def test_publish_flyr_sd(self):
        if self.gis.properties.isPortal:
            self.skipTest(
                "Specific service definition file not able to publish to Kubernetes."
            )
        svcdef_file = get_resource_path(
            relative_path="staging_data/item_class_test_data/ago_multilyr_svc_grplyr_x4j2.sd",
            verify=True,
            unique_copy=True,
        )

        svcdef_item = self.item_test_publish_folder.add(
            item_properties=ItemProperties(
                title="ago_multilyr_svc_grplyr_map",
                item_type=ItemTypeEnum.SERVICE_DEFINITION,
                snippet="Service definition file added with Folder in api.",
                description="Service definition file for Python API integration testing.",
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=svcdef_file,
        ).result()

        svcdef_flyr_item = svcdef_item.publish(
            publish_parameters={"name": "ago_multilyr_svc_grplyr_map_api"}
        )

        self.assertEqual(
            svcdef_item.type,
            "Service Definition",
            "Service definition item not returning correct value for type property.",
        )
        self.assertTrue(
            svcdef_flyr_item, "Failed to publish feature layer from service definition."
        )
        self.assertIsInstance(
            svcdef_flyr_item, Item, "Publish opertaion did not result in an item."
        )
        self.assertEqual(
            svcdef_flyr_item.type,
            "Feature Service",
            "Publishing service definition does not create Feature Service item.",
        )
        self.assertTrue(
            len(svcdef_flyr_item.layers) == 3,
            "Publishing item did not create 3 layers as expected in Feature Service.",
        )
        self.assertIsInstance(
            svcdef_flyr_item.layers[0],
            FeatureLayer,
            "Feature Layer item layers property not returning a FeatureLayer object.",
        )
        self.assertGreater(
            svcdef_flyr_item.layers[0].query(return_count_only=True),
            0,
            "Feature Service layer does not have features as expected.",
        )
    @unittest.skip("for now")
    def test_publish_tlyr_sd(self):
        if self.gis.properties.isPortal:
            self.skipTest(
                "Specific service definition publishes to ArcGIS Online only."
            )
        svcdef_tile_file = get_resource_path(
            relative_path="staging_data/item_class_test_data/agors_simpleTiled.sd",
            verify=True,
            unique_copy=True,
        )
        svcdef_tile_pkg_item = self.item_test_publish_folder.add(
            item_properties=ItemProperties(
                title="ago_Tile_QueryLayer",
                item_type=ItemTypeEnum.SERVICE_DEFINITION,
                snippet="Service definition item created with API.",
                description="Service definition used for integration testing.",
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=svcdef_tile_file,
        ).result()

        svcdef_tile_lyr_item = svcdef_tile_pkg_item.publish(
            publish_parameters={"name": "ago_tile_querylayer_api"},
            build_initial_cache=True,
        )

        self.assertEqual(
            svcdef_tile_pkg_item.type,
            "Service Definition",
            "Service definition item not returning correct value for type property.",
        )
        time.sleep(180)
        self.assertTrue(
            svcdef_tile_lyr_item,
            "Failed to publish tile layer from service definition.",
        )
        self.assertIsInstance(
            svcdef_tile_lyr_item, Item, "Publish opertaion did not result in an item."
        )
        self.assertEqual(
            svcdef_tile_lyr_item.type,
            "Map Service",
            "Publishing service definition does not create Feature Service item.",
        )
        self.assertTrue(
            len(svcdef_tile_lyr_item.layers) == 3,
            "Publishing item did not create 3 layers as expected in Map Service.",
        )
    @unittest.skip("for now")
    def test_publish_shp(self):
        shp_source_file = get_resource_path(
            relative_path="staging_data/USA_Major_Cities.zip",
            verify=True,
            unique_copy=True,
        )
        shp_item = self.item_test_publish_folder.add(
            item_properties=ItemProperties(
                title="usa_major_cities_itemtest",
                item_type=ItemTypeEnum.SHAPEFILE,
                snippet="Shapefile item added with Folder in API.",
                description="Shapefile item for Python API integration testing.",
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=shp_source_file,
        ).result()
        shp_flyr_item = shp_item.publish(
            publish_parameters={"name": "usa_major_cities_itemtest_api"}
        )
        self.assertEqual(
            shp_item.type,
            "Shapefile",
            "Shapefile item not returning correct value for type property.",
        )
        self.assertIsNotNone(shp_flyr_item, "Failed to publish shapefile layer.")
        self.assertEqual(
            len(shp_flyr_item.layers), 1, "Shapefile layer item should have 1 layer."
        )
        self.assertIsInstance(
            shp_flyr_item.layers[0],
            FeatureLayer,
            "Feature Layer item layers property not returning a FeatureLayer object.",
        )
        self.assertGreater(
            shp_flyr_item.layers[0].query(return_count_only=True),
            0,
            "Shapefile layer does not have features as expected.",
        )


if __name__ == "__main__":
    unittest.main()
