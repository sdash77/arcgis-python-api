#-------------------------------------------------------------------------------
# Name:        FeatureLayerCollectionManager class tests
# Purpose:     Tests for reading, editing FeatureLayerCollection definitions and
#                overwriting hosted feature services
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import os
import datetime

#region PreCondition check
test_skip = False
class_skip = False
module_skip = False

r1 = PreconditionChecks.check_API_import()
r2 = PreconditionChecks.check_Python_version()

if (r1 & r2):
    print("## Precondition checks passed ##")
    module_skip = False
else:
    module_skip = True
    print("Pre condition checks failed. Quitting tests")
    raise(exit())

# Import the module after Precondition checks pass
try:
    import arcgis
    from arcgis.gis import GIS
    from arcgis import features
    from arcgis.features.managers import FeatureLayerCollectionManager
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Features module")
def setUpModule():
    """
    Set up code for full arcgis.features module FeatureLayerCollectionManager class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_FeatureLayerCollectionManager_portal(unittest.TestCase):
    """
    Test to check if a FeatureLayerCollectionManager object works with builtin portal
    """
    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """

        #region Read config data
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['datascienceqa']['url']
        cls.portal_username = _conf_reader['datascienceqa']['admin_user']
        cls.portal_password = _conf_reader['datascienceqa']['admin_password']

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_FeatureLayerCollectionManager_cls']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password, verify_cert=False)
        if cls.gis is None:
            cls.class_skip = True
        #endregion

        # region Publish the feature layer if it does not exist
        cls.namePrefix = "dino_FeatureLayerCollectionManager_"
        layer_name = cls.namePrefix + "basic"

        search_result = PortalUtils.search_portal_item(cls.gis, layer_name, "Feature Layer")
        if search_result is not None:
            print("Found necessary feature layer")
            cls.feature_layer1_item = search_result
        else:
            print("Cannot find necessary feature layer, publishing a new layer")
            csv_path = cls.qalab_cls_path + 'simple_points.csv'
            csv_item = cls.gis.content.add({'title': layer_name}, data=csv_path)

            # publish the csv item
            if csv_item is not None:
                cls.feature_layer1_item = csv_item.publish({'name': layer_name})
                if cls.feature_layer1_item is not None:
                    print("Published edit_feature_definition_points feature layer")
                else:
                    print("Failed to publish csv to feature layer")
                    class_skip = True
            else:
                print("Failed to add necessary csv file to portal")
                class_skip = True
        # endregion

        print("==================================================================")
        print("Beginning tests in Test_FeatureLayer_portal class")

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_FeatureLayerCollectionManager_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_create_FeatureLayerCollectionManager_object(self):
        """
        Purpose of this test is to create instances of FeatureLayerCollectionManager class in multiple ways
        :return:
        """
        try:
            test_item = self.feature_layer1_item
            self.assertIsInstance(test_item, arcgis.gis.Item, "Input item is not of type Item, "
                                                              "cannot run rest of the test case")

            #check a FeatureLayerCollectionManager object can be created from url
            flcm_url = FeatureLayerCollectionManager(test_item.url, self.gis)
            self.assertIsInstance(flcm_url, arcgis.features.managers.FeatureLayerCollectionManager,
                                  "Cannot create a FeatureLayerCollectionManager obj from url")

            #check FeatureLayerCollectionManager object can be created from item
            flcm_item = FeatureLayerCollectionManager.fromitem(test_item)
            self.assertIsInstance(flcm_item, arcgis.features.managers.FeatureLayerCollectionManager,
                                  "Cannot create a FeatureLayerCollectionManager from item")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_overwrite_HFS_using_csv(self):
        """
        Publish a feature layer with csv.
        Update the csv and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region publish feature layer if not found
        data_item = PortalUtils.search_portal_item(self.gis, "set1_overwrite_HFS_csv", "CSV")
        if data_item is None:
            # upload data item
            data_path = os.path.join(self.qalab_cls_path, "set1_overwrite_HFS_csv.csv")
            data_item = self.gis.content.add({}, data=data_path)
            self.assertIsNotNone(data_item, "Cannot add data item")

        wfl_item = PortalUtils.search_portal_item(self.gis, "set1_overwrite_HFS_csv", "Feature Service")
        if wfl_item is None:
            # publish the data item
            wfl_item = data_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish data into a feature service")
        # endregion

        # region delete all features in feature layer
        flayer = wfl_item.layers[0]
        delete_result = flayer.delete_features(where="1=1")
        self.assertIsNotNone(delete_result, "Unable to delete features before ovewrite")
        num_features_after_delete = flayer.query(return_count_only=True)
        self.assertEqual(num_features_after_delete, 0, "Num features not 0 after delete all")
        # endregion

        try:
            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(wfl_item)

            # overwrite the feature layer
            new_data_path = os.path.join(self.qalab_cls_path, "overwrite_wfl", "set1_overwrite_HFS_csv.csv")
            overwrite_result = flc_mgr.overwrite(new_data_path)
            self.assertIsNotNone(overwrite_result, "Calling publish with overwrite True returns None")

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(num_features_after_overwrite, 0, "Overwrite failed to add new features")

            # verify number of features and attributes
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            self.assertEqual((20, 8), overwritten_flayer_df.shape,
                             "The number of rows cols of overwritten feature layer is not more than original")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_overwrite_HFS_using_fgdb(self):
        """
        Publish a feature layer with file geodatabase.
        Update the fgdb and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region publish feature layer if not found
        fgdb_item = PortalUtils.search_portal_item(self.gis, "title:set1_overwrite_HFS_fgdb.gdb",
                                                "File Geodatabase")
        if fgdb_item is None:
            # upload fgdb item
            fgdb_path = os.path.join(self.qalab_cls_path, "set1_overwrite_HFS_fgdb.gdb.zip")
            fgdb_item = self.gis.content.add({}, data=fgdb_path)
            self.assertIsNotNone(fgdb_item, "Cannot add fgdb item")

        wfl_item = PortalUtils.search_portal_item(self.gis, "set1_overwrite_HFS_fgdb", "Feature Service")
        if wfl_item is None:
            # publish the fgdb item
            wfl_item = fgdb_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish fgdb into a feature service")
        # endregion

        # region delete all features in feature layer
        flayer = wfl_item.layers[0]
        delete_result = flayer.delete_features(where="1=1")
        self.assertIsNotNone(delete_result, "Unable to delete features before ovewrite")
        num_features_after_delete = flayer.query(return_count_only=True)
        self.assertEqual(num_features_after_delete, 0, "Num features not 0 after delete all")
        #endregion

        try:
            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(wfl_item)

            # overwrite the feature layer
            new_fgdb_path = os.path.join(self.qalab_cls_path, "overwrite_wfl",
                                         "set1_overwrite_HFS_fgdb.gdb.zip")
            overwrite_result = flc_mgr.overwrite(new_fgdb_path)
            self.assertIsNotNone(overwrite_result, "Calling publish with overwrite True returns None")

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(num_features_after_overwrite, 0, "Overwrite failed to add new features")

            #verify number of features and attributes
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            self.assertEqual((20, 8), overwritten_flayer_df.shape,
                             "The number of rows cols of overwritten feature layer is not more than original")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_overwrite_HFS_using_shp(self):
        """
        Publish a feature layer with shape file
        Update the shp and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region publish feature layer if not found
        data_item = PortalUtils.search_portal_item(self.gis, "title:set1_overwrite_HFS_shp", "Shapefile")
        if data_item is None:
            # upload shp item
            data_path = os.path.join(self.qalab_cls_path, "set1_overwrite_HFS_shp.zip")
            data_item = self.gis.content.add({}, data=data_path)
            self.assertIsNotNone(data_item, "Cannot add data item")

        wfl_item = PortalUtils.search_portal_item(self.gis, "set1_overwrite_HFS_shp", "Feature Service")
        if wfl_item is None:
            # publish the data item
            wfl_item = data_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish data into a feature service")
        # endregion

        # region delete all features in feature layer
        flayer = wfl_item.layers[0]
        delete_result = flayer.delete_features(where="1=1")
        self.assertIsNotNone(delete_result, "Unable to delete features before ovewrite")
        num_features_after_delete = flayer.query(return_count_only=True)
        self.assertEqual(num_features_after_delete, 0, "Num features not 0 after delete all")
        # endregion

        try:
            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(wfl_item)

            # overwrite the feature layer
            new_data_path = os.path.join(self.qalab_cls_path, "overwrite_wfl", "set1_overwrite_HFS_shp.zip")
            overwrite_result = flc_mgr.overwrite(new_data_path)
            self.assertIsNotNone(overwrite_result, "Calling publish with overwrite True returns None")

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(num_features_after_overwrite, 0, "Overwrite failed to add new features")

            # verify number of features and attributes
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            self.assertEqual((20, 8), overwritten_flayer_df.shape,
                             "The number of rows cols of overwritten feature layer is not more than original")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_overwrite_HFS_using_sd(self):
        """
        Publish a feature layer with SD file
        Update the sd with another SD that is not marked for overwriting and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region publish feature layer if not found
        data_item = PortalUtils.search_portal_item(self.gis, "title:set1_overwrite_HFS_sd", "Service Definition")
        if data_item is None:
            # upload data item
            data_path = os.path.join(self.qalab_cls_path, "set1_overwrite_HFS_sd.sd")
            data_item = self.gis.content.add({}, data=data_path)
            self.assertIsNotNone(data_item, "Cannot add data item")

        wfl_item = PortalUtils.search_portal_item(self.gis, "set1_overwrite_HFS_sd", "Feature Service")
        if wfl_item is None:
            # publish the data item
            wfl_item = data_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish data into a feature service")
        # endregion

        # region delete all features in feature layer
        flayer = wfl_item.layers[0]
        delete_result = flayer.delete_features(where="1=1")
        self.assertIsNotNone(delete_result, "Unable to delete features before ovewrite")
        num_features_after_delete = flayer.query(return_count_only=True)
        self.assertEqual(num_features_after_delete, 0, "Num features not 0 after delete all")
        # endregion

        try:
            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(wfl_item)

            # overwrite the feature layer
            new_data_path = os.path.join(self.qalab_cls_path, "overwrite_wfl", "set1_overwrite_HFS_sd.sd")
            overwrite_result = flc_mgr.overwrite(new_data_path)
            self.assertIsNotNone(overwrite_result, "Calling publish with overwrite True returns None")

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(num_features_after_overwrite, 0, "Overwrite failed to add new features")

            # verify number of features and attributes
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            self.assertEqual((20, 8), overwritten_flayer_df.shape,
                             "The number of rows cols of overwritten feature layer is not more than original")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

class Test_FeatureLayerCollectionManager_online(unittest.TestCase):
    """
    Test to check if a FeatureLayerCollectionManager object works with ArcGIS Online
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """

        # region Read config data
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['arcgiscom']['url']
        cls.portal_username = _conf_reader['arcgiscom']['admin_user']
        cls.portal_password = _conf_reader['arcgiscom']['admin_password']

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data'][
            'qalab_FeatureLayerCollectionManager_cls']
        # endregion

        # region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        if cls.gis is None:
            cls.class_skip = True
        # endregion

        # region Publish the feature layer if it does not exist
        # cls.namePrefix = "dino_FeatureLayerCollectionManager_"
        # layer_name = cls.namePrefix + "basic"
        #
        # search_result = PortalUtils.search_portal_item(cls.gis, layer_name, "Feature Layer")
        # if search_result is not None:
        #     print("Found necessary feature layer")
        #     cls.feature_layer1_item = search_result
        # else:
        #     print("Cannot find necessary feature layer, publishing a new layer")
        #     csv_path = cls.qalab_cls_path + 'simple_points.csv'
        #     csv_item = PortalUtils.search_portal_item(cls.gis, 'simple_points.csv', 'CSV')
        #     if not csv_item:
        #         csv_item = cls.gis.content.add({'title': layer_name}, data=csv_path)
        #
        #     # publish the csv item
        #     if csv_item is not None:
        #         cls.feature_layer1_item = csv_item.publish({'title': layer_name})
        #         if cls.feature_layer1_item is not None:
        #             print("Published edit_feature_definition_points feature layer")
        #         else:
        #             print("Failed to publish csv to feature layer")
        #             class_skip = True
        #     else:
        #         print("Failed to add necessary csv file to portal")
        #         class_skip = True
        # endregion

        print("==================================================================")
        print("Beginning tests in Test_FeatureLayer_portal class")

    def setUp(self):
        test_skip = False  # reset the skip flag
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_FeatureLayerCollectionManager_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
                                     str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_create_FeatureLayerCollectionManager_object(self):
        """
        Purpose of this test is to create instances of FeatureLayerCollectionManager class in multiple ways
        :return:
        """
        try:
            # test_item = self.feature_layer1_item
            test_item = self.gis.content.get('7566e0221e5646f99ea249a197116605')
            # https://www.arcgis.com/home/item.html?id=7566e0221e5646f99ea249a197116605
            self.assertIsInstance(test_item, arcgis.gis.Item, "Input item is not of type Item, "
                                                              "cannot run rest of the test case")

            # check a FeatureLayerCollectionManager object can be created from url
            flcm_url = FeatureLayerCollectionManager(test_item.url, self.gis)
            self.assertIsInstance(flcm_url, arcgis.features.managers.FeatureLayerCollectionManager,
                                  "Cannot create a FeatureLayerCollectionManager obj from url")

            # check FeatureLayerCollectionManager object can be created from item
            flcm_item = FeatureLayerCollectionManager.fromitem(test_item)
            self.assertIsInstance(flcm_item, arcgis.features.managers.FeatureLayerCollectionManager,
                                  "Cannot create a FeatureLayerCollectionManager from item")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_overwrite_HFS_using_csv(self):
        """
        Publish a feature layer with csv.
        Update the csv and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region publish feature layer if not found
        data_item = PortalUtils.search_portal_item(self.gis, "set1_overwrite_HFS_csv", "CSV")
        if data_item is None:
            # upload data item
            data_path = os.path.join(self.qalab_cls_path, "set1_overwrite_HFS_csv.csv")
            data_item = self.gis.content.add({}, data=data_path)
            self.assertIsNotNone(data_item, "Cannot add data item")

        wfl_item = PortalUtils.search_portal_item(self.gis, "set1_overwrite_HFS_csv", "Feature Service")
        if wfl_item is None:
            # publish the data item
            wfl_item = data_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish data into a feature service")
        # endregion

        # region delete all features in feature layer
        flayer = wfl_item.layers[0]
        delete_result = flayer.delete_features(where="1=1")
        self.assertIsNotNone(delete_result, "Unable to delete features before ovewrite")
        num_features_after_delete = flayer.query(return_count_only=True)
        self.assertEqual(num_features_after_delete, 0, "Num features not 0 after delete all")
        # endregion

        try:
            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(wfl_item)

            # overwrite the feature layer
            new_data_path = os.path.join(self.qalab_cls_path, "overwrite_wfl", "set1_overwrite_HFS_csv.csv")
            overwrite_result = flc_mgr.overwrite(new_data_path)
            self.assertIsNotNone(overwrite_result, "Calling publish with overwrite True returns None")

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(num_features_after_overwrite, 0, "Overwrite failed to add new features")

            # verify number of features and attributes
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            self.assertEqual((20, 8), overwritten_flayer_df.shape,
                             "The number of rows cols of overwritten feature layer is not more than original")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_overwrite_HFS_using_fgdb(self):
        """
        Publish a feature layer with file geodatabase.
        Update the fgdb and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region publish feature layer if not found
        fgdb_item = PortalUtils.search_portal_item(self.gis, "title:set1_overwrite_HFS_fgdb.gdb",
                                                "File Geodatabase")
        if fgdb_item is None:
            # upload fgdb item
            fgdb_path = os.path.join(self.qalab_cls_path, "set1_overwrite_HFS_fgdb.gdb.zip")
            fgdb_item = self.gis.content.add({}, data=fgdb_path)
            self.assertIsNotNone(fgdb_item, "Cannot add fgdb item")

        wfl_item = PortalUtils.search_portal_item(self.gis, "set1_overwrite_HFS_fgdb", "Feature Service")
        if wfl_item is None:
            # publish the fgdb item
            wfl_item = fgdb_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish fgdb into a feature service")
        # endregion

        # region delete all features in feature layer
        flayer = wfl_item.layers[0]
        delete_result = flayer.delete_features(where="1=1")
        self.assertIsNotNone(delete_result, "Unable to delete features before ovewrite")
        num_features_after_delete = flayer.query(return_count_only=True)
        self.assertEqual(num_features_after_delete, 0, "Num features not 0 after delete all")
        #endregion

        try:
            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(wfl_item)

            # overwrite the feature layer
            new_fgdb_path = os.path.join(self.qalab_cls_path, "overwrite_wfl",
                                         "set1_overwrite_HFS_fgdb.gdb.zip")
            overwrite_result = flc_mgr.overwrite(new_fgdb_path)
            self.assertIsNotNone(overwrite_result, "Calling publish with overwrite True returns None")

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(num_features_after_overwrite, 0, "Overwrite failed to add new features")

            #verify number of features and attributes
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            self.assertEqual((20, 8), overwritten_flayer_df.shape,
                             "The number of rows cols of overwritten feature layer is not more than original")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_overwrite_HFS_using_shp(self):
        """
        Publish a feature layer with shape file
        Update the shp and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region publish feature layer if not found
        data_item = PortalUtils.search_portal_item(self.gis, "title:set1_overwrite_HFS_shp", "Shapefile")
        if data_item is None:
            # upload shp item
            data_path = os.path.join(self.qalab_cls_path, "set1_overwrite_HFS_shp.zip")
            data_item = self.gis.content.add({}, data=data_path)
            self.assertIsNotNone(data_item, "Cannot add data item")

        wfl_item = PortalUtils.search_portal_item(self.gis, "set1_overwrite_HFS_shp", "Feature Service")
        if wfl_item is None:
            # publish the data item
            wfl_item = data_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish data into a feature service")
        # endregion

        # region delete all features in feature layer
        flayer = wfl_item.layers[0]
        delete_result = flayer.delete_features(where="1=1")
        self.assertIsNotNone(delete_result, "Unable to delete features before ovewrite")
        num_features_after_delete = flayer.query(return_count_only=True)
        self.assertEqual(num_features_after_delete, 0, "Num features not 0 after delete all")
        #endregion

        try:
            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(wfl_item)

            # overwrite the feature layer
            new_data_path = os.path.join(self.qalab_cls_path, "overwrite_wfl", "set1_overwrite_HFS_shp.zip")
            overwrite_result = flc_mgr.overwrite(new_data_path)
            self.assertIsNotNone(overwrite_result, "Calling publish with overwrite True returns None")

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(num_features_after_overwrite, 0, "Overwrite failed to add new features")

            #verify number of features and attributes
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            self.assertEqual((20, 8), overwritten_flayer_df.shape,
                             "The number of rows cols of overwritten feature layer is not more than original")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_overwrite_HFS_using_sd(self):
        """
        Publish a feature layer with SD file
        Update the sd with another SD that is not marked for overwriting and overwrite the feature service.
        Ensure the contents are updated, itemid remains same.
        :return:
        """
        # region publish feature layer if not found
        data_item = PortalUtils.search_portal_item(self.gis, "title:set1_overwrite_HFS_sd", "Service Definition")
        if data_item is None:
            # upload data item
            data_path = os.path.join(self.qalab_cls_path, "set1_overwrite_HFS_sd.sd")
            data_item = self.gis.content.add({}, data=data_path)
            self.assertIsNotNone(data_item, "Cannot add data item")

        wfl_item = PortalUtils.search_portal_item(self.gis, "set1_overwrite_HFS_sd", "Feature Service")
        if wfl_item is None:
            # publish the data item
            wfl_item = data_item.publish()
            self.assertIsNotNone(wfl_item, "Cannot publish data into a feature service")
        # endregion

        # region delete all features in feature layer
        flayer = wfl_item.layers[0]
        delete_result = flayer.delete_features(where="1=1")
        self.assertIsNotNone(delete_result, "Unable to delete features before ovewrite")
        num_features_after_delete = flayer.query(return_count_only=True)
        self.assertEqual(num_features_after_delete, 0, "Num features not 0 after delete all")
        # endregion

        try:
            # access feature layer coll manager
            flc_mgr = FeatureLayerCollectionManager.fromitem(wfl_item)

            # overwrite the feature layer
            new_data_path = os.path.join(self.qalab_cls_path, "overwrite_wfl", "set1_overwrite_HFS_sd.sd")
            overwrite_result = flc_mgr.overwrite(new_data_path)
            self.assertIsNotNone(overwrite_result, "Calling publish with overwrite True returns None")

            # verify content is updated
            num_features_after_overwrite = flayer.query(return_count_only=True)
            self.assertGreater(num_features_after_overwrite, 0, "Overwrite failed to add new features")

            # verify number of features and attributes
            fset = flayer.query()
            overwritten_flayer_df = fset.sdf

            # add two extra columns to account for x,y geometries that get added
            self.assertEqual((20, 8), overwritten_flayer_df.shape,
                             "The number of rows cols of overwritten feature layer is not more than original")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

#TestModule
def tearDownModule():
    print("**End GIS module Tests**")