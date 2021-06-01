#-------------------------------------------------------------------------------
# Name:        FeatureLayer class tests
# Purpose:     Tests for reading feature layers, editing them.
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
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
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Features module")
def setUpModule():
    """
    Set up code for full arcgis.features module Featurelayer class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_FeatureLayer_portal(unittest.TestCase):
    """
    Test to check if a FeatureLayer object works with builtin portal
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
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_FeatureLayer_cls']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        if cls.gis is None:
            cls.class_skip = True
        #endregion

        #region Publish the feature layer if it does not exist
        cls.namePrefix = "dino_FeatureLayer_"
        layer_name = cls.namePrefix + "basic"

        search_result = PortalUtils.search_portal_item(cls.gis, layer_name, "Feature Layer")
        if search_result is not None:
            print("Found necessary feature layer")
            cls.feature_layer1_item = search_result
        else:
            print("Cannot find necessary feature layer, publishing a new layer")
            search_result = PortalUtils.search_portal_item(cls.gis, layer_name, "CSV")
            if search_result is not None:
                csv_item = search_result
            else:
                csv_path = cls.qalab_cls_path + 'edit_features_points.csv'
                csv_item = cls.gis.content.add({'title':layer_name}, data = csv_path)

            #publish the csv item
            if csv_item is not None:
                cls.feature_layer1_item = csv_item.publish({'title':layer_name})
                if cls.feature_layer1_item is not None:
                    print("Published edit_features_points feature layer")
                else:
                    print("Failed to publish csv to feature layer")
                    class_skip = True
            else:
                print("Failed to add necessary csv file to portal")
                class_skip = True

        # ensure feature layer has necessary capabilities enabled
        flc = features.FeatureLayerCollection.fromitem(cls.feature_layer1_item)
        if flc is not None:
            if 'Editing' not in flc.properties.capabilities:
                result = flc.manager.update_definition({'capabilities':'Create,Delete,Query,Update,Editing,Extract',
                                               'syncEnabled':True})
                if result.get('success'):
                    print("Enabled necessary capabilities on feature layer")
                else:
                    print(str(result))
                    class_skip = True
        else:
            print("Cannot create a FeatureLayerCollection manager class")
            class_skip = True
        #endregion

        # region Publish the feature layer for delete_features if it does not exist
        cls.namePrefix = "dino_FeatureLayer_"
        layer_name_delfeatures = cls.namePrefix + "delfeatures"

        search_result = PortalUtils.search_portal_item(cls.gis, layer_name_delfeatures, "Feature Layer")
        if search_result is not None:
            print("Found necessary feature layer")
            cls.feature_layer2_item = search_result
        else:
            print("Cannot find necessary feature layer, publishing a new layer")
            fgdb_path = cls.qalab_cls_path + 'set1_fortune10_delfeatures.gdb.zip'
            fgdb_item = cls.gis.content.add({'title': layer_name_delfeatures}, data=fgdb_path)

            # publish the csv item
            if fgdb_item is not None:
                cls.feature_layer2_item = fgdb_item.publish()
                if cls.feature_layer2_item is not None:
                    print("Published dino_FeatureLayer_delfeatures feature layer")
                else:
                    print("Failed to publish data item to feature layer")
                    class_skip = True
            else:
                print("Failed to add necessary data item file to portal")
                class_skip = True

        # ensure feature layer has necessary capabilities enabled
        flc = features.FeatureLayerCollection.fromitem(cls.feature_layer2_item)
        if flc is not None:
            if 'Editing' not in flc.properties.capabilities:
                result = flc.manager.update_definition(
                    {'capabilities': 'Create,Delete,Query,Update,Editing,Extract',
                     'syncEnabled': True})
                if result.get('success'):
                    print("Enabled necessary capabilities on feature layer")
                else:
                    print(str(result))
                    class_skip = True
        else:
            print("Cannot create a FeatureLayerCollection manager class")
            class_skip = True
            # endregion

        #endregion
        print("==================================================================")
        print("Beginning tests in Test_FeatureLayer_portal class")
        #endregion

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        # self.namePrefix = "dino_FeatureLayer_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    def test_feature_mod_classes(self):
        """
        Purpose of this test is to obtain main objects in feature module and verify their types are correct.
        :return:
        """
        try:
            test_item = self.feature_layer1_item
            self.assertIsInstance(test_item, arcgis.gis.Item, "Input item is not of type Item, cannot run rest of the test case")

            #check Item.layers property yields a list of FeatureLayer objects
            flayers = test_item.layers
            self.assertIsInstance(flayers, list, "Item.layers property does not return a list")
            self.assertIsInstance(flayers[0], arcgis.features.FeatureLayer, "Item.layers property does not return a list of FeatureLayer objects")

            #check a FeatureLayerCollection object can be created from Item object
            flc = features.FeatureLayerCollection.fromitem(test_item)
            self.assertIsInstance(flc, arcgis.features.FeatureLayerCollection, "Cannot create a FeatureLayerCollection obj from FeatureLayer Item")

            #check FeatureLayer objects be obtained from FLC
            flayers2 = flc.layers
            self.assertIsInstance(flayers2, list, "FeatureLayerCollection.layers property does not return a list")
            self.assertIsInstance(flayers2[0], arcgis.features.FeatureLayer,
                                  "FeatureLayerCollection.layers property does not return a list of FeatureLayer objects")

            #check FeatureSet can be obtained from FeatureLayer object
            flayer1 = flayers[0]
            fset = flayer1.query()
            self.assertIsInstance(fset, arcgis.features.FeatureSet, "FeatureLayer.query() does not return a FeatureSet obj")

            #check Feature objects be obtained from FeatureSet object
            feature_list = fset.features
            self.assertIsInstance(feature_list, list, "FeatureSet.features does not return a list")
            f1 = feature_list[0]
            self.assertIsInstance(f1, arcgis.features.Feature, "FeatureSet.features does not return a list of Feature objects")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_edit_features_updates(self):
        try:
            #access the feature layer and its feature for editing
            flayers = self.feature_layer1_item.layers
            flayer0 = flayers[0]
            fset = flayer0.query("city_ID=1")
            flist = fset.features

            self.assertGreater(len(flist),0, "Cannot search for features")
            f1 = flist[0]

            #prepare for editing
            f1.attributes['timestamp_'] = self.time_stamp
            update_result = flayer0.edit_features(updates = [f1])

            self.assertIsNotNone(update_result, "Calling edit_features returns none")

            #ensure edit success
            self.assertTrue(update_result['updateResults'][0]['success'], "Update fails")

            fset_post_update = flayer0.query('city_ID=1')
            f1_post_update = fset_post_update.features[0]

            self.assertEqual(f1_post_update.attributes['timestamp_'], self.time_stamp, "Updates are not reflected in the feature layer")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_feature_query_as_df_classes(self):
        """
        Purpose of this test is to check if feature layer can be queried as a dataframe
        :return:
        """
        try:
            # access the feature layer and its feature for editing
            flayers = self.feature_layer1_item.layers
            flayer0 = flayers[0]
            county_featureset = flayer0.query(as_df=True)
            from pandas import core
            self.assertIsInstance(county_featureset, core.frame.DataFrame, "FeatureLayer.query(as_df=True) does not return a DataFrame obj")
            self.assertEqual(5, county_featureset.shape[0], "Number of features not correct")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(class_skip, "Preconditions not met, skipping test")
    def test_delete_features(self):
        try:
            # access the feature layer and its feature for editing
            flayers = self.feature_layer2_item.layers
            flayer0 = flayers[0]

            # add two features
            f1 = features.Feature()
            f1.geometry = {'x': -9785223.91346784, 'y': 5317966.588194862}
            f1.attributes = {'CITY': 'MILWAUKEE', 'STATE': 'WI', 'X': -87.902162, 'Y': 43.039372}

            f2 = features.Feature()
            f2.attributes = {'CITY': 'ORLANDO', 'STATE': 'FL', 'X': -81.404424, 'Y': 28.47029}
            f2.geometry = {'x': -9061899.027999733, 'y': 3308397.032848168}

            # push 2 features to service
            flayer0.edit_features(adds=[f1, f2])

            # get count after adding 2 features
            old_feature_count = flayer0.query(return_count_only=True)
            self.assertGreater(old_feature_count, 0,
                               "At least 2 features should be present in feature layer, none present")

            # delete all features
            delete_features_result = flayer0.delete_features(where='1=1')
            self.assertIsNotNone(delete_features_result, "Got back none from delete_features method call")
            self.assertGreater(len(delete_features_result['deleteResults']), 0, "Length of delete_features call result "
                                                                                "is 0. Did not delete even 1 feature.")

            # Verify number of features after truncate
            new_feature_count = flayer0.query(return_count_only=True)
            self.assertEqual(new_feature_count, 0, "Feature count after delete_features not equal to 0")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

class Test_FeatureLayer_kubernetes(unittest.TestCase):
    """
    Test to check if a FeatureLayer object works with builtin portal
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

        cls.portal_url = _conf_reader['kubeportal']['url']
        cls.portal_username = _conf_reader['kubeportal']['admin_user']
        cls.portal_password = _conf_reader['kubeportal']['admin_password']

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_FeatureLayer_cls']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        if cls.gis is None:
            cls.class_skip = True
        #endregion

        #region Publish the feature layer if it does not exist
        cls.namePrefix = "dino_FeatureLayer_"
        layer_name = cls.namePrefix + "basic"

        search_result = PortalUtils.search_portal_item(cls.gis, layer_name, "Feature Layer")
        if search_result is not None:
            print("Found necessary feature layer")
            cls.feature_layer1_item = search_result
        else:
            print("Cannot find necessary feature layer, publishing a new layer")
            search_result = PortalUtils.search_portal_item(cls.gis, layer_name, "CSV")
            if search_result is not None:
                csv_item = search_result
            else:
                csv_path = cls.qalab_cls_path + 'edit_features_points.csv'
                csv_item = cls.gis.content.add({'title':layer_name}, data = csv_path)

            #publish the csv item
            if csv_item is not None:
                cls.feature_layer1_item = csv_item.publish({'title':layer_name})
                if cls.feature_layer1_item is not None:
                    print("Published edit_features_points feature layer")
                else:
                    print("Failed to publish csv to feature layer")
                    class_skip = True
            else:
                print("Failed to add necessary csv file to portal")
                class_skip = True

        # ensure feature layer has necessary capabilities enabled
        flc = features.FeatureLayerCollection.fromitem(cls.feature_layer1_item)
        if flc is not None:
            if 'Editing' not in flc.properties.capabilities:
                result = flc.manager.update_definition({'capabilities':'Create,Delete,Query,Update,Editing,Extract',
                                               'syncEnabled':True})
                if result.get('success'):
                    print("Enabled necessary capabilities on feature layer")
                else:
                    print(str(result))
                    class_skip = True
        else:
            print("Cannot create a FeatureLayerCollection manager class")
            class_skip = True
        #endregion

        # region Publish the feature layer for delete_features if it does not exist
        cls.namePrefix = "dino_FeatureLayer_"
        layer_name_delfeatures = cls.namePrefix + "delfeatures"

        search_result = PortalUtils.search_portal_item(cls.gis, layer_name_delfeatures, "Feature Layer")
        if search_result is not None:
            print("Found necessary feature layer")
            cls.feature_layer2_item = search_result
        else:
            print("Cannot find necessary feature layer, publishing a new layer")
            fgdb_path = cls.qalab_cls_path + 'set1_fortune10_delfeatures.gdb.zip'
            fgdb_item = cls.gis.content.add({'title': layer_name_delfeatures}, data=fgdb_path)

            # publish the csv item
            if fgdb_item is not None:
                cls.feature_layer2_item = fgdb_item.publish()
                if cls.feature_layer2_item is not None:
                    print("Published dino_FeatureLayer_delfeatures feature layer")
                else:
                    print("Failed to publish data item to feature layer")
                    class_skip = True
            else:
                print("Failed to add necessary data item file to portal")
                class_skip = True

        # ensure feature layer has necessary capabilities enabled
        flc = features.FeatureLayerCollection.fromitem(cls.feature_layer2_item)
        if flc is not None:
            if 'Editing' not in flc.properties.capabilities:
                result = flc.manager.update_definition(
                    {'capabilities': 'Create,Delete,Query,Update,Editing,Extract',
                     'syncEnabled': True})
                if result.get('success'):
                    print("Enabled necessary capabilities on feature layer")
                else:
                    print(str(result))
                    class_skip = True
        else:
            print("Cannot create a FeatureLayerCollection manager class")
            class_skip = True
            # endregion

        #endregion
        print("==================================================================")
        print("Beginning tests in Test_FeatureLayer_kubernetes class")
        #endregion

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        # self.namePrefix = "dino_FeatureLayer_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    def test_feature_mod_classes(self):
        """
        Purpose of this test is to obtain main objects in feature module and verify their types are correct.
        :return:
        """
        try:
            test_item = self.feature_layer1_item
            self.assertIsInstance(test_item, arcgis.gis.Item, "Input item is not of type Item, cannot run rest of the test case")

            #check Item.layers property yields a list of FeatureLayer objects
            flayers = test_item.layers
            self.assertIsInstance(flayers, list, "Item.layers property does not return a list")
            self.assertIsInstance(flayers[0], arcgis.features.FeatureLayer, "Item.layers property does not return a list of FeatureLayer objects")

            #check a FeatureLayerCollection object can be created from Item object
            flc = features.FeatureLayerCollection.fromitem(test_item)
            self.assertIsInstance(flc, arcgis.features.FeatureLayerCollection, "Cannot create a FeatureLayerCollection obj from FeatureLayer Item")

            #check FeatureLayer objects be obtained from FLC
            flayers2 = flc.layers
            self.assertIsInstance(flayers2, list, "FeatureLayerCollection.layers property does not return a list")
            self.assertIsInstance(flayers2[0], arcgis.features.FeatureLayer,
                                  "FeatureLayerCollection.layers property does not return a list of FeatureLayer objects")

            #check FeatureSet can be obtained from FeatureLayer object
            flayer1 = flayers[0]
            fset = flayer1.query()
            self.assertIsInstance(fset, arcgis.features.FeatureSet, "FeatureLayer.query() does not return a FeatureSet obj")

            #check Feature objects be obtained from FeatureSet object
            feature_list = fset.features
            self.assertIsInstance(feature_list, list, "FeatureSet.features does not return a list")
            f1 = feature_list[0]
            self.assertIsInstance(f1, arcgis.features.Feature, "FeatureSet.features does not return a list of Feature objects")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_edit_features_updates(self):
        try:
            #access the feature layer and its feature for editing
            flayers = self.feature_layer1_item.layers
            flayer0 = flayers[0]
            fset = flayer0.query("city_ID=1")
            flist = fset.features

            self.assertGreater(len(flist),0, "Cannot search for features")
            f1 = flist[0]

            #prepare for editing
            f1.attributes['timestamp_'] = self.time_stamp
            update_result = flayer0.edit_features(updates = [f1])

            self.assertIsNotNone(update_result, "Calling edit_features returns none")

            #ensure edit success
            self.assertTrue(update_result['updateResults'][0]['success'], "Update fails")

            fset_post_update = flayer0.query('city_ID=1')
            f1_post_update = fset_post_update.features[0]

            self.assertEqual(f1_post_update.attributes['timestamp_'], self.time_stamp, "Updates are not reflected in the feature layer")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_feature_query_as_df_classes(self):
        """
        Purpose of this test is to check if feature layer can be queried as a dataframe
        :return:
        """
        try:
            # access the feature layer and its feature for editing
            flayers = self.feature_layer1_item.layers
            flayer0 = flayers[0]
            county_featureset = flayer0.query(as_df=True)
            from pandas import core
            self.assertIsInstance(county_featureset, core.frame.DataFrame, "FeatureLayer.query(as_df=True) does not return a DataFrame obj")
            self.assertEqual(5, county_featureset.shape[0], "Number of features not correct")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(class_skip, "Preconditions not met, skipping test")
    def test_delete_features(self):
        try:
            # access the feature layer and its feature for editing
            flayers = self.feature_layer2_item.layers
            flayer0 = flayers[0]

            # add two features
            f1 = features.Feature()
            f1.geometry = {'x': -9785223.91346784, 'y': 5317966.588194862}
            f1.attributes = {'CITY': 'MILWAUKEE', 'STATE': 'WI', 'X': -87.902162, 'Y': 43.039372}

            f2 = features.Feature()
            f2.attributes = {'CITY': 'ORLANDO', 'STATE': 'FL', 'X': -81.404424, 'Y': 28.47029}
            f2.geometry = {'x': -9061899.027999733, 'y': 3308397.032848168}

            # push 2 features to service
            flayer0.edit_features(adds=[f1, f2])

            # get count after adding 2 features
            old_feature_count = flayer0.query(return_count_only=True)
            self.assertGreater(old_feature_count, 0,
                               "At least 2 features should be present in feature layer, none present")

            # delete all features
            delete_features_result = flayer0.delete_features(where='1=1')
            self.assertIsNotNone(delete_features_result, "Got back none from delete_features method call")
            self.assertGreater(len(delete_features_result['deleteResults']), 0, "Length of delete_features call result "
                                                                                "is 0. Did not delete even 1 feature.")

            # Verify number of features after truncate
            new_feature_count = flayer0.query(return_count_only=True)
            self.assertEqual(new_feature_count, 0, "Feature count after delete_features not equal to 0")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

class Test_FeatureLayer_online(unittest.TestCase):
    """
    Test to check if a FeatureLayer object works with builtin portal
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

        cls.portal_url = _conf_reader['arcgiscom']['url']
        cls.portal_username = _conf_reader['arcgiscom']['admin_user']
        cls.portal_password = _conf_reader['arcgiscom']['admin_password']

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_FeatureLayer_cls']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        if cls.gis is None:
            cls.class_skip = True
        #endregion

        #region Publish the feature layer if it does not exist
        cls.namePrefix = "dino_FeatureLayer_"
        layer_name = cls.namePrefix + "basic"

        search_result = PortalUtils.search_portal_item(cls.gis, layer_name, "Feature Layer")
        if search_result is not None:
            print("Found necessary feature layer")
            cls.feature_layer1_item = search_result
        else:
            print("Cannot find necessary feature layer, publishing a new layer")
            search_result = PortalUtils.search_portal_item(cls.gis, layer_name, "CSV")
            if search_result is not None:
                csv_item = search_result
            else:
                csv_path = cls.qalab_cls_path + 'edit_features_points.csv'
                csv_item = cls.gis.content.add({'title':layer_name}, data = csv_path)

            #publish the csv item
            if csv_item is not None:
                cls.feature_layer1_item = csv_item.publish()
                if cls.feature_layer1_item is not None:
                    print("Published edit_features_points feature layer")
                else:
                    print("Failed to publish csv to feature layer")
                    class_skip = True
            else:
                print("Failed to add necessary csv file to portal")
                class_skip = True

        # ensure feature layer has necessary capabilities enabled
        flc = features.FeatureLayerCollection.fromitem(cls.feature_layer1_item)
        if flc is not None:
            if 'Editing' not in flc.properties.capabilities:
                result = flc.manager.update_definition(
                    {"hasStaticData": False,
                     'capabilities':'Create,Delete,Query,Update,Editing,Extract',
                     'syncEnabled':True})
                if result.get('success'):
                    print("Enabled necessary capabilities on feature layer")
                else:
                    print(str(result))
                    class_skip = True
        else:
            print("Cannot create a FeatureLayerCollection manager class")
            class_skip = True
        #endregion

        # region Publish the feature layer for delete_features if it does not exist
        cls.namePrefix = "dino_FeatureLayer_"
        layer_name_delfeatures = cls.namePrefix + "delfeatures"

        search_result = PortalUtils.search_portal_item(cls.gis, layer_name_delfeatures, "Feature Layer")
        if search_result is not None:
            print("Found necessary feature layer")
            cls.feature_layer2_item = search_result
        else:
            print("Cannot find necessary feature layer, publishing a new layer")
            fgdb_path = cls.qalab_cls_path + 'set1_fortune10_delfeatures.gdb.zip'
            fgdb_item = cls.gis.content.add({'title': layer_name_delfeatures}, data=fgdb_path)

            # publish the csv item
            if fgdb_item is not None:
                cls.feature_layer2_item = fgdb_item.publish()
                if cls.feature_layer2_item is not None:
                    print("Published dino_FeatureLayer_delfeatures feature layer")
                else:
                    print("Failed to publish data item to feature layer")
                    class_skip = True
            else:
                print("Failed to add necessary data item file to portal")
                class_skip = True

        # ensure feature layer has necessary capabilities enabled
        flc = features.FeatureLayerCollection.fromitem(cls.feature_layer2_item)
        if flc is not None:
            if 'Editing' not in flc.properties.capabilities:
                result = flc.manager.update_definition(
                    {"hasStaticData": False,
                     'capabilities': 'Create,Delete,Query,Update,Editing,Extract',
                     'syncEnabled': True})
                if result.get('success'):
                    print("Enabled necessary capabilities on feature layer")
                else:
                    print(str(result))
                    class_skip = True
        else:
            print("Cannot create a FeatureLayerCollection manager class")
            class_skip = True
            # endregion

        #endregion
        print("==================================================================")
        print("Beginning tests in Test_FeatureLayer_online class")
        #endregion

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        # self.namePrefix = "dino_FeatureLayer_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    def test_feature_mod_classes(self):
        """
        Purpose of this test is to obtain main objects in feature module and verify their types are correct.
        :return:
        """
        try:
            test_item = self.feature_layer1_item
            self.assertIsInstance(test_item, arcgis.gis.Item, "Input item is not of type Item, cannot run rest of the test case")

            #check Item.layers property yields a list of FeatureLayer objects
            flayers = test_item.layers
            self.assertIsInstance(flayers, list, "Item.layers property does not return a list")
            self.assertIsInstance(flayers[0], arcgis.features.FeatureLayer, "Item.layers property does not return a list of FeatureLayer objects")

            #check a FeatureLayerCollection object can be created from Item object
            flc = features.FeatureLayerCollection.fromitem(test_item)
            self.assertIsInstance(flc, arcgis.features.FeatureLayerCollection, "Cannot create a FeatureLayerCollection obj from FeatureLayer Item")

            #check FeatureLayer objects be obtained from FLC
            flayers2 = flc.layers
            self.assertIsInstance(flayers2, list, "FeatureLayerCollection.layers property does not return a list")
            self.assertIsInstance(flayers2[0], arcgis.features.FeatureLayer,
                                  "FeatureLayerCollection.layers property does not return a list of FeatureLayer objects")

            #check FeatureSet can be obtained from FeatureLayer object
            flayer1 = flayers[0]
            fset = flayer1.query()
            self.assertIsInstance(fset, arcgis.features.FeatureSet, "FeatureLayer.query() does not return a FeatureSet obj")

            #check Feature objects be obtained from FeatureSet object
            feature_list = fset.features
            self.assertIsInstance(feature_list, list, "FeatureSet.features does not return a list")
            f1 = feature_list[0]
            self.assertIsInstance(f1, arcgis.features.Feature, "FeatureSet.features does not return a list of Feature objects")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_edit_features_updates(self):
        try:
            #access the feature layer and its feature for editing
            flayers = self.feature_layer1_item.layers
            flayer0 = flayers[0]
            fset = flayer0.query("city_ID=1")
            flist = fset.features

            self.assertGreater(len(flist),0, "Cannot search for features")
            f1 = flist[0]

            #prepare for editing
            f1.attributes['POP2000'] = 37000
            update_result = flayer0.edit_features(updates=[f1])
            # f1.attributes['timestamp_'] = self.time_stamp
            # update_result = flayer0.edit_features(updates=[f1])

            self.assertIsNotNone(update_result, "Calling edit_features returns none")

            #ensure edit success
            self.assertTrue(update_result['updateResults'][0]['success'], "Update fails")

            fset_post_update = flayer0.query('city_ID=1')
            f1_post_update = fset_post_update.features[0]

            self.assertEqual(f1_post_update.attributes['POP2000'], 37000, "Updates are not reflected in the feature layer")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(class_skip, "Preconditions not met, skipping test")
    def test_delete_features(self):
        try:
            # access the feature layer and its feature for editing
            flayers = self.feature_layer2_item.layers
            flayer0 = flayers[0]

            # add two features
            f1 = features.Feature()
            f1.geometry = {'x': -9785223.91346784, 'y': 5317966.588194862}
            f1.attributes = {'CITY': 'MILWAUKEE', 'STATE': 'WI', 'X': -87.902162, 'Y': 43.039372}

            f2 = features.Feature()
            f2.attributes = {'CITY': 'ORLANDO', 'STATE': 'FL', 'X': -81.404424, 'Y': 28.47029}
            f2.geometry = {'x': -9061899.027999733, 'y': 3308397.032848168}

            # push 2 features to service
            flayer0.edit_features(adds=[f1, f2])

            # get count after adding 2 features
            old_feature_count = flayer0.query(return_count_only=True)
            self.assertGreater(old_feature_count, 0,
                               "At least 2 features should be present in feature layer, none present")

            # delete all features
            delete_features_result = flayer0.delete_features(where='1=1')
            self.assertIsNotNone(delete_features_result, "Got back none from delete_features method call")
            self.assertGreater(len(delete_features_result['deleteResults']), 0, "Length of delete_features call result "
                                                                                "is 0. Did not delete even 1 feature.")

            # Verify number of features after truncate
            new_feature_count = flayer0.query(return_count_only=True)
            self.assertEqual(new_feature_count, 0, "Feature count after delete_features not equal to 0")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_feature_query_classes(self):
        """
        Purpose of this test is to obtain main objects in feature module and verify their types are correct.
        :return:
        """
        try:
            from arcgis.features import FeatureLayer
            county_layer = FeatureLayer(
                "https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/test_FGDB/FeatureServer/0")
            county_featureset = county_layer.query()
            self.assertIsInstance(county_featureset, arcgis.features.FeatureSet, "FeatureLayer.query() does not return a FeatureSet obj")
            self.assertEqual(100, len(county_featureset.features), "Number of features not correct")

            #check Feature objects be obtained from FeatureSet object
            feature_list = county_featureset.features
            self.assertIsInstance(feature_list, list, "FeatureSet.features does not return a list")
            f1 = feature_list[0]
            self.assertIsInstance(f1, arcgis.features.Feature, "FeatureSet.features does not return a list of Feature objects")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_feature_query_as_df_classes(self):
        """
        Purpose of this test is to obtain main objects in feature module and verify their types are correct.
        :return:
        """
        try:
            from arcgis.features import FeatureLayer
            county_layer = FeatureLayer(
                "https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/test_FGDB/FeatureServer/0")
            county_featureset = county_layer.query(as_df=True)
            from pandas import core
            self.assertIsInstance(county_featureset, core.frame.DataFrame, "FeatureLayer.query(as_df=True) does not return a DataFrame obj")
            self.assertEqual(100, county_featureset.shape[0], "Number of features not correct")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

# TestModule

def tearDownModule():
    print("**End GIS module Tests**")


    ########################################################################
    # The feature service end points for  tests below do not work.
    # Query and query as dataframe functionality is being tested above.
    # Commenting out the code below for future use.
    ########################################################################

    # def test_feature_excessive_query_classes(self):
    #     """
    #     Purpose of this test is to obtain main objects in feature module and verify their types are correct.
    #     :return:
    #     """
    #     try:
    #         from arcgis.features import FeatureLayer
    #         county_layer = FeatureLayer(
    #             "https://demographics8.arcgis.com/arcgis/rest/services/USA_Demographics_and_Boundaries_2018/MapServer/14")
    #         county_featureset = county_layer.query()
    #         self.assertIsInstance(county_featureset, arcgis.features.FeatureSet, "FeatureLayer.query() does not return a FeatureSet obj")
    #         self.assertEqual(32196, len(county_featureset.features), "Number of features not correct")
    #
    #         #check Feature objects be obtained from FeatureSet object
    #         feature_list = county_featureset.features
    #         self.assertIsInstance(feature_list, list, "FeatureSet.features does not return a list")
    #         f1 = feature_list[0]
    #         self.assertIsInstance(f1, arcgis.features.Feature, "FeatureSet.features does not return a list of Feature objects")
    #
    #     except AssertionError as assertErrorException:
    #         test_skip = True
    #         raise assertErrorException
    #
    #     except unittest.SkipTest as skipException:
    #         raise skipException
    #
    #     except Exception as testException:
    #         self.fail("Error during test: " + testException.__str__())
    #
    # def test_feature_excessive_query_as_df_classes(self):
    #     """
    #     Purpose of this test is to obtain main objects in feature module and verify their types are correct.
    #     :return:
    #     """
    #     try:
    #         from arcgis.features import FeatureLayer
    #         county_layer = FeatureLayer(
    #             "https://demographics8.arcgis.com/arcgis/rest/services/USA_Demographics_and_Boundaries_2018/MapServer/14")
    #         county_featureset = county_layer.query(as_df=True)
    #         from pandas import core
    #         self.assertIsInstance(county_featureset, core.frame.DataFrame, "FeatureLayer.query(as_df=True) does not return a DataFrame obj")
    #         self.assertEqual(32196, county_featureset.shape[0], "Number of features not correct")
    #
    #     except AssertionError as assertErrorException:
    #         test_skip = True
    #         raise assertErrorException
    #
    #     except unittest.SkipTest as skipException:
    #         raise skipException
    #
    #     except Exception as testException:
    #         self.fail("Error during test: " + testException.__str__())
    #
    # def test_feature_external_query_as_df_classes(self):
    #     """
    #     Purpose of this test is to obtain main objects in feature module and verify their types are correct.
    #     :return:
    #     """
    #     try:
    #         from arcgis.features import FeatureLayer
    #         county_layer = FeatureLayer(
    #             "https://gisdev.odf.oregon.gov/gisdev/rest/services/GeoEvent/VaisalaLightning/FeatureServer/0")
    #         county_featureset = county_layer.query(as_df=True)
    #         from pandas import core
    #         self.assertIsInstance(county_featureset, core.frame.DataFrame, "FeatureLayer.query(as_df=True) does not return a DataFrame obj")
    #         self.assertEqual(3396, county_featureset.shape[0], "Number of features not correct")
    #
    #     except AssertionError as assertErrorException:
    #         test_skip = True
    #         raise assertErrorException
    #
    #     except unittest.SkipTest as skipException:
    #         raise skipException
    #
    #     except Exception as testException:
    #         self.fail("Error during test: " + testException.__str__())
    #
    # def test_feature_geoevent_query_as_df_classes(self):
    #     """
    #     Purpose of this test is to obtain main objects in feature module and verify their types are correct.
    #     :return:
    #     """
    #     try:
    #         from arcgis.features import FeatureLayer
    #         county_layer = FeatureLayer(
    #             "https://services8.arcgis.com/mpSDBlkEzjS62WgX/arcgis/rest/services/WorkerPosition/FeatureServer/1")
    #         # county_featureset = county_layer.query()
    #         # self.assertIsInstance(county_featureset, arcgis.features.FeatureSet, "FeatureLayer.query() does not return a FeatureSet obj")
    #         # self.assertEqual(37784, len(county_featureset.features), "Number of features not correct")
    #         county_featureset = county_layer.query(as_df=True)
    #         from pandas import core
    #         self.assertIsInstance(county_featureset, core.frame.DataFrame, "FeatureLayer.query(as_df=True) does not return a DataFrame obj")
    #         self.assertEqual(44538, county_featureset.shape[0], "Number of features not correct")
    #
    #     except AssertionError as assertErrorException:
    #         test_skip = True
    #         raise assertErrorException
    #
    #     except unittest.SkipTest as skipException:
    #         raise skipException
    #
    #     except Exception as testException:
    #         self.fail("Error during test: " + testException.__str__())

