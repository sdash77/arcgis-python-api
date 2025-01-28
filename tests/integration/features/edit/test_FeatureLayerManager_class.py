# -------------------------------------------------------------------------------
# Name:        FeatureLayerManager class tests
# Purpose:     Tests for reading, editing FeatureLayer definitions
# -------------------------------------------------------------------------------
import unittest
import os
import datetime
import arcgis
from arcgis.gis import GIS
from arcgis import features
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test, profiles


@profiles.enterprise_and_agol
@integration_test
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
        cls.items = []
        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_cls_path = os.path.join(
            cls.qalab_base_path, "features_mod_FeatureLayerManager_cls"
        )

        # region Publish the feature layer if it does not exist
        cls.namePrefix = "dino_FeatureLayerManager"
        layer_name_basic = f"{cls.namePrefix}_basic"
        csv_path = os.path.join(
            cls.qalab_cls_path, "edit_feature_definition_points_test.csv"
        )

        cls.feature_layer_item = cls.publish_test_item(
            cls.gis, layer_name_basic, "Feature Layer", csv_path
        )

        # endregion

        # region Publish the feature layer for truncate if it does not exist
        cls.namePrefix = "dino_FeatureLayerManager_"
        layer_name_truncate = cls.namePrefix + "truncate"
        fgdb_path = os.path.join(
            cls.qalab_cls_path, "set1_fortune10_trunc2_FLMtest.gdb.zip"
        )

        cls.feature_layer_item_truncate = cls.publish_test_item(
            cls.gis, layer_name_truncate, "Feature Layer", fgdb_path
        )

    def setUp(self):
        test_skip = False  # reset the skip flag
        print("Test: " + self._testMethodName)
        # self.namePrefix = "dino_FeatureLayer_"

        t = datetime.datetime.now()
        self.time_stamp = str.format(
            "Time stamp: {0}_{1}_{2}_{3}_{4}_{5}",
            str(t.year),
            str(t.month),
            str(t.day),
            str(t.hour),
            str(t.minute),
            str(t.second),
        )
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        rel_items = cls.feature_layer_item.related_items("Service2Data", "forward")
        for rel_item in rel_items:
            rel_item.delete(permanent=True)
        cls.feature_layer_item.delete(permanent=True)
        rel_trunc_items = cls.feature_layer_item_truncate.related_items(
            "Service2Data", "forward"
        )
        for rel_trunc_item in rel_trunc_items:
            rel_trunc_item.delete(permanent=True)
        cls.feature_layer_item_truncate.delete(permanent=True)

    def test_create_FeatureLayerManager_object(self):
        """
        Purpose of this test is to create instances of FeatureLayerManager class in multiple ways
        :return:
        """
        try:
            test_item = self.feature_layer_item
            self.assertIsInstance(
                test_item,
                arcgis.gis.Item,
                "Input item is not of type Item, cannot run rest of the test case",
            )

            # check Item.layers property yields a list of FeatureLayer objects
            flayers = test_item.layers
            self.assertIsInstance(
                flayers, list, "Item.layers property does not return a list"
            )
            self.assertIsInstance(
                flayers[0],
                arcgis.features.FeatureLayer,
                "Item.layers property does not return a list of FeatureLayer objects",
            )

            # check a FeatureLayerManager object can be created from FeatureLayer object
            flayer0 = flayers[0]
            flayer0_mgr = flayer0.manager
            self.assertIsInstance(
                flayer0_mgr,
                arcgis.features.managers.FeatureLayerManager,
                "Cannot create a FeatureLayerCollection obj from FeatureLayer Item",
            )

            # check FeatureLayerManager object can be created from item
            flm2 = features.managers.FeatureLayerManager.fromitem(test_item)
            self.assertIsInstance(
                flm2,
                arcgis.features.managers.FeatureLayerManager,
                "FeatureLayerManager.fromitem() method does not create a manager object",
            )

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
            # access the feature layer and its feature for editing
            flayers = self.feature_layer_item.layers
            flayer0 = flayers[0]
            flm = flayer0.manager

            # get template field
            existing_fields = flm.properties.fields
            template_field = dict(deepcopy(existing_fields[1]))

            # prepare the new field
            template_field["alias"] = self.time_stamp.replace(" ", "_").replace(":", "")
            template_field["name"] = (
                self.time_stamp.replace(" ", "_").replace(":", "").lower()
            )

            # add the new field
            add_result = flm.add_to_definition({"fields": [template_field]})

            self.assertIsNotNone(add_result, "Calling add_to_definition returns none")

            # ensure edit success
            self.assertTrue(add_result["success"], "adding new field fails")

            # ensure new field is added
            flm._refresh()
            new_fields = flm.properties.fields
            self.assertGreater(
                len(new_fields),
                len(existing_fields),
                "Number of fields did not increase",
            )

            # ensure the last field is the one we added
            last_field = new_fields[-1]
            self.assertEqual(
                last_field.name,
                template_field["name"],
                "The last field name does not match timestamp",
            )

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
            flayers = self.feature_layer_item.layers
            flayer0 = flayers[0]
            flm = flayer0.manager

            # ensure there are enough fields
            existing_fields = flm.properties.fields
            if len(existing_fields) < 2:
                raise unittest.SkipTest(
                    "Number of fields in this layer is too few to test deletion"
                )

            last_field = dict(deepcopy(existing_fields[-1]))

            # delete the last field
            delete_result = flm.delete_from_definition({"fields": [last_field]})

            self.assertIsNotNone(
                delete_result, "Calling delete_from_definition returns none"
            )

            # ensure edit success
            self.assertTrue(delete_result["success"], "adding new field fails")

            # ensure last field is dropped
            flm._refresh()
            new_fields = flm.properties.fields
            self.assertLess(
                len(new_fields),
                len(existing_fields),
                "Number of fields did not decrease",
            )

            # ensure the last field is not the one we dropped
            new_last_field = new_fields[-1]
            self.assertNotEqual(
                new_last_field.name,
                last_field["name"],
                "The last field name should be different from what we dropped",
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + str(testException))

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
            flayers = self.feature_layer_item_truncate.layers
            flayer0 = flayers[0]
            flm = flayer0.manager

            # add two features
            f1 = features.Feature()
            f1.geometry = {"x": -9785223.91346784, "y": 5317966.588194862}
            f1.attributes = {
                "CITY": "MILWAUKEE",
                "STATE": "WI",
                "X": -87.902162,
                "Y": 43.039372,
            }

            f2 = features.Feature()
            f2.attributes = {
                "CITY": "ORLANDO",
                "STATE": "FL",
                "X": -81.404424,
                "Y": 28.47029,
            }
            f2.geometry = {"x": -9061899.027999733, "y": 3308397.032848168}

            # push 2 features to service
            flayer0.edit_features(adds=[f1, f2])

            # get count after adding 2 features
            old_feature_count = flayer0.query(return_count_only=True)
            self.assertGreater(
                old_feature_count,
                0,
                "At least 2 features should be present in feature layer, none present",
            )

            # truncate table - actual test
            truncate_result = flm.truncate()
            self.assertIsNotNone(
                truncate_result, "Got back none from truncate method call"
            )
            self.assertTrue(truncate_result["success"], "truncate failed")

            # Verify number of features after truncate
            new_feature_count = flayer0.query(return_count_only=True)
            self.assertEqual(
                new_feature_count, 0, "Feature count after truncate not equal to 0"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @classmethod
    def publish_test_item(
        cls, gis: GIS, layer_name: str, item_type: str, source_data_path: str
    ):
        # Clean out existing items
        item_types = ["CSV", "File Geodatabase", "Feature Layer"]
        for itm_type in item_types:
            search_result = gis.content.search(layer_name, item_type=itm_type)
            for search_item in search_result:
                search_item.delete(permanent=True)
        try:
            root_folder = gis.content.folders.get()
            source_item = root_folder.add(
                item_properties={
                    "title": layer_name,
                    "type": (
                        "CSV"
                        if source_data_path[-3:].upper() == "CSV"
                        else "File Geodatabase"
                    ),
                    "tags": "integration-test",
                    "snippet": "Item for Feature Layer integration testing",
                },
                file=source_data_path,
            ).result()
            # publish the item
            if source_item is not None:
                feature_layer_item = source_item.publish(
                    {"name": layer_name, "tags": "integration-test"}
                )
                if feature_layer_item is not None:
                    print("Published edit_feature_definition_points feature layer")
                    is_prepped_for_editing = cls.prep_test_item(feature_layer_item)
                    if is_prepped_for_editing:
                        return feature_layer_item
                    else:
                        raise Exception("Could not update editing capabilities")
        except Exception as ex:
            print("Failed to add necessary item file to portal", ex)

    @classmethod
    def prep_test_item(cls, feature_layer):
        # ensure feature layer has necessary capabilities enabled
        flc = features.FeatureLayerCollection.fromitem(feature_layer)
        if flc is not None:
            if "Editing" in flc.properties.capabilities:
                return True
            else:
                result = flc.manager.update_definition(
                    {
                        "capabilities": "Create,Delete,Query,Update,Editing,Extract,Sync",
                    }
                )
                return result


# TestModule
def tearDownModule():
    print("**End GIS module Tests**")


if __name__ == "__main__":
    unittest.main()
