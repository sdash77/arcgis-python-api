#-------------------------------------------------------------------------------
# Name:        FeatureLayerManager class tests
# Purpose:     Tests for reading, editing FeatureLayer definitions
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

class Test_FeatureLayerManager_portal(unittest.TestCase):
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

        cls.portal_url = _conf_reader['teamportal']['url']
        cls.portal_username = _conf_reader['teamportal']['admin_user']
        cls.portal_password = _conf_reader['teamportal']['admin_password']

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_FeatureLayerManager_cls']
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
        cls.namePrefix = "dino_FeatureLayerManager_"
        layer_name = cls.namePrefix + "basic"

        search_result = PortalUtils.search_portal_item(cls.gis, layer_name, "Feature Layer")
        if search_result is not None:
            print("Found necessary feature layer")
            cls.feature_layer1_item = search_result
        else:
            print("Cannot find necessary feature layer, publishing a new layer")
            csv_path = cls.qalab_cls_path + 'edit_feature_definition_points.csv'
            csv_item = cls.gis.content.add({'title':layer_name}, data = csv_path)

            #publish the csv item
            if csv_item is not None:
                cls.feature_layer1_item = csv_item.publish({'title':layer_name})
                if cls.feature_layer1_item is not None:
                    print("Published edit_feature_definition_points feature layer")
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

        # region Publish the feature layer for truncate if it does not exist
        cls.namePrefix = "dino_FeatureLayerManager_"
        layer_name_truncate = cls.namePrefix + "truncate"

        search_result = PortalUtils.search_portal_item(cls.gis, layer_name_truncate, "Feature Layer")
        if search_result is not None:
            print("Found necessary feature layer")
            cls.feature_layer2_item = search_result
        else:
            print("Cannot find necessary feature layer, publishing a new layer")
            fgdb_path = cls.qalab_cls_path + 'set1_fortune10_trunc2.gdb.zip'
            fgdb_item = cls.gis.content.add({'title': layer_name_truncate}, data=fgdb_path)

            # publish the csv item
            if fgdb_item is not None:
                cls.feature_layer2_item = fgdb_item.publish()
                if cls.feature_layer2_item is not None:
                    print("Published set1_fortune10_trunc feature layer")
                else:
                    print("Failed to publish csv to feature layer")
                    class_skip = True
            else:
                print("Failed to add necessary csv file to portal")
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
        #endregion

        #region print banner
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

    def test_create_FeatureLayerManager_object(self):
        """
        Purpose of this test is to create instances of FeatureLayerManager class in multiple ways
        :return:
        """
        try:
            test_item = self.feature_layer1_item
            self.assertIsInstance(test_item, arcgis.gis.Item, "Input item is not of type Item, cannot run rest of the test case")

            #check Item.layers property yields a list of FeatureLayer objects
            flayers = test_item.layers
            self.assertIsInstance(flayers, list, "Item.layers property does not return a list")
            self.assertIsInstance(flayers[0], arcgis.features.FeatureLayer,
                                  "Item.layers property does not return a list of FeatureLayer objects")

            #check a FeatureLayerManager object can be created from FeatureLayer object
            flayer0 = flayers[0]
            flayer0_mgr = flayer0.manager
            self.assertIsInstance(flayer0_mgr, arcgis.features.managers.FeatureLayerManager,
                                  "Cannot create a FeatureLayerCollection obj from FeatureLayer Item")

            #check FeatureLayerManager object can be created from item
            flm2 = features.managers.FeatureLayerManager.fromitem(test_item)
            self.assertIsInstance(flm2, arcgis.features.managers.FeatureLayerManager,
                                  "FeatureLayerManager.fromitem() method does not create a manager object")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_add_to_definition(self):
        """
        This test case adds new fields to a feature layer using the FeatureLayerManager
        class' add_to_definition() method
        :return:
        """
        from copy import deepcopy
        try:
            #access the feature layer and its feature for editing
            flayers = self.feature_layer1_item.layers
            flayer0 = flayers[0]
            flm = flayer0.manager

            #get template field
            existing_fields = flm.properties.fields
            template_field = dict(deepcopy(existing_fields[1]))

            #prepare the new field
            template_field['alias'] = self.time_stamp.replace(" ","_").replace(":","")
            template_field['name'] = self.time_stamp.replace(" ","_").replace(":","").lower()

            #add the new field
            add_result = flm.add_to_definition({'fields':[template_field]})

            self.assertIsNotNone(add_result, "Calling add_to_definition returns none")

            #ensure edit success
            self.assertTrue(add_result['success'], "adding new field fails")

            #ensure new field is added
            flm._refresh()
            new_fields = flm.properties.fields
            self.assertGreater(len(new_fields), len(existing_fields), "Number of fields did not increase")

            #ensure the last field is the one we added
            last_field = new_fields[-1]
            self.assertEqual(last_field.name, template_field['name'], "The last field name does not match timestamp")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_delete_from_definition(self):
        """
        This test case deletes the last field from a feature layer using the FeatureLayerManager
        class' delete_from_definition() method
        :return:
        """
        from copy import deepcopy
        try:
            # access the feature layer and its feature for editing
            flayers = self.feature_layer1_item.layers
            flayer0 = flayers[0]
            flm = flayer0.manager

            # ensure there are enough fields
            existing_fields = flm.properties.fields
            if len(existing_fields) < 2:
                raise unittest.SkipTest("Number of fields in this layer is too few to test deletion")


            last_field = dict(deepcopy(existing_fields[-1]))

            # delete the last field
            delete_result = flm.delete_from_definition({'fields': [last_field]})

            self.assertIsNotNone(delete_result, "Calling delete_from_definition returns none")

            # ensure edit success
            self.assertTrue(delete_result['success'], "adding new field fails")

            # ensure last field is dropped
            flm._refresh()
            new_fields = flm.properties.fields
            self.assertLess(len(new_fields), len(existing_fields), "Number of fields did not decrease")

            # ensure the last field is not the one we dropped
            new_last_field = new_fields[-1]
            self.assertNotEqual(new_last_field.name, last_field['name'],
                             "The last field name should be different from what we dropped")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

    @unittest.skipIf(True, "Yet to fix bug for portals. Works for AGO")
    def test_truncate_feature_layer(self):
        """
        This test case calls truncate() which will drop all features in 1 go.
        First we edit the feature layer by adding at least 2 features. Then call truncate to drop all features and 
        verify the number of features.
        :return:
        """
        from copy import deepcopy
        try:
            # access the feature layer and its feature for editing
            flayers = self.feature_layer2_item.layers
            flayer0 = flayers[0]
            flm = flayer0.manager

            # add two features
            f1 = features.Feature()
            f1.geometry ={'x': -9785223.91346784, 'y': 5317966.588194862}
            f1.attributes = {'CITY': 'MILWAUKEE', 'STATE': 'WI', 'X': -87.902162, 'Y': 43.039372}

            f2 = features.Feature()
            f2.attributes = {'CITY': 'ORLANDO', 'STATE': 'FL', 'X': -81.404424, 'Y': 28.47029}
            f2.geometry ={'x': -9061899.027999733, 'y': 3308397.032848168}

            #push 2 features to service
            flayer0.edit_features(adds = [f1, f2])

            # get count after adding 2 features
            old_feature_count = flayer0.query(return_count_only=True)
            self.assertGreater(old_feature_count, 0, "At least 2 features should be present in feature layer, none present")

            # truncate table - actual test
            truncate_result = flm.truncate()
            self.assertIsNotNone(truncate_result, "Got back none from truncate method call")
            self.assertTrue(truncate_result['success'], "truncate failed")

            # Verify number of features after truncate
            new_feature_count = flayer0.query(return_count_only=True)
            self.assertEqual(new_feature_count, 0, "Feature count after truncate not equal to 0")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

#TestModule
def tearDownModule():
    print("**End GIS module Tests**")