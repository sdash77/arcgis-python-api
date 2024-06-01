import os
import unittest
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer, FeatureLayerCollection, FeatureSet, Feature
from pandas import DataFrame
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test, profiles

@profiles.admin_all
@integration_test
class TestFeatureLayerClass(unittest.TestCase):
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
        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_cls_path = os.path.join(
            cls.qalab_base_path, "features_mod_FeatureLayer_cls"
        )
        cls.namePrefix = "dino_FeatureLayer_"

        # Publish feature layer if it does not exist
        layer_name = cls.namePrefix + "basic"

        search_fl = cls.gis.content.search(layer_name, "Feature Layer")
        if search_fl:
            cls.feature_layer1_item = search_fl[0]
        else:
            search_csv = cls.gis.content.search(layer_name, "CSV")
            if search_csv:
                csv_item = search_csv[0]
            else:
                csv_path = os.path.join(cls.qalab_cls_path, "edit_features_points.csv")
                csv_item = cls.gis.content.add({"title": layer_name}, data=csv_path)
            cls.feature_layer1_item = csv_item.publish({"title": layer_name})
            assert isinstance(cls.feature_layer1_item, Item)

        # ensure feature layer has necessary capabilities enabled
        flc = FeatureLayerCollection.fromitem(cls.feature_layer1_item)
        if "Editing" not in flc.properties.capabilities:
            result = flc.manager.update_definition(
                {
                    "capabilities": "Create,Delete,Query,Update,Editing,Extract,Sync",
                }
            )
            if result.get("success"):
                print("Enabled necessary capabilities on feature layer")
            else:
                print(str(result))

        # Publish feature layer for delete_features if it does not exist
        layer_name_delfeatures = cls.namePrefix + "delfeatures"

        search_result = cls.gis.content.search(layer_name_delfeatures, "Feature Layer")
        if search_result:
            cls.feature_layer2_item = search_result[0]
        else:
            fgdb_path = os.path.join(
                cls.qalab_cls_path, "set1_fortune10_delfeatures.gdb.zip"
            )
            fgdb_item = cls.gis.content.add(
                {"title": layer_name_delfeatures}, data=fgdb_path
            )
            cls.feature_layer2_item = fgdb_item.publish(
                {"name": layer_name_delfeatures}
            )
            assert isinstance(cls.feature_layer2_item, Item)

        flc_del = FeatureLayerCollection.fromitem(cls.feature_layer2_item)
        if "Editing" not in flc_del.properties.capabilities:
            result = flc.manager.update_definition(
                {
                    "capabilities": "Create,Delete,Query,Update,Editing,Extract,Sync",
                }
            )
            if result.get("success"):
                print("Enabled necessary capabilities on feature layer")
            else:
                print(str(result))

    def test_feature_mod_classes(self):
        """
        Purpose of this test is to obtain main objects in feature module and verify their types are correct.
        :return:
        """
        # check Item.layers property yields a list of FeatureLayer objects
        flayers = self.feature_layer1_item.layers
        assert isinstance(flayers, list)
        assert isinstance(flayers[0], FeatureLayer)

        # check a FeatureLayerCollection object can be created from Item object thru fromitem()
        flc = FeatureLayerCollection.fromitem(self.feature_layer1_item)
        assert isinstance(flc, FeatureLayerCollection)

        # check FeatureLayer objects are obtained from FLC thru layers property
        flayers_flc = flc.layers
        assert isinstance(flayers_flc, list)
        assert isinstance(flayers_flc[0], FeatureLayer)

        # check FeatureSet can be obtained from FeatureLayer object thru query()
        fset = flayers[0].query()
        assert isinstance(fset, FeatureSet)

        # check Feature objects be obtained from FeatureSet object thru features property
        feature_list = fset.features
        assert isinstance(feature_list, list)
        assert isinstance(feature_list[0], Feature)

    def test_edit_features_updates(self):
        """
        Test for updating features with edit_features()
        """
        # access the feature layer and its feature for editing
        flayer0 = self.feature_layer1_item.layers[0]
        fset = self.feature_layer1_item.layers[0].query("city_ID=1")
        f1 = fset.features[0]

        # update thru edit_feature()
        update_result = flayer0.edit_features(updates=[f1])
        print(update_result)
        assert update_result.get("updateResults")[0].get("success")

    def test_feature_query_as_df_classes(self):
        """
        Purpose of this test is to check if feature layer can be queried as a dataframe
        :return:
        """
        flayer0 = self.feature_layer1_item.layers[0]
        county_fs_df = flayer0.query(as_df=True)
        assert isinstance(county_fs_df, DataFrame)
        self.assertEqual(5, county_fs_df.shape[0], "Number of features not correct")

    def test_delete_features(self):
        """
        test for deleting features with edit_features()
        """
        # access the feature layer and its feature for editing
        flayer0 = self.feature_layer2_item.layers[0]

        # add two features
        f1 = Feature()
        f1.geometry = {"x": -9785223.91346784, "y": 5317966.588194862}
        f1.attributes = {
            "CITY": "MILWAUKEE",
            "STATE": "WI",
            "X": -87.902162,
            "Y": 43.039372,
        }

        f2 = Feature()
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

        # delete all features
        delete_features_result = flayer0.delete_features(where="1=1")
        print(delete_features_result)
        assert delete_features_result.get("deleteResults")[0].get("success")

        # Verify number of features after truncate
        new_feature_count = flayer0.query(return_count_only=True)
        self.assertEqual(
            new_feature_count,
            0,
            "Feature count after delete_features not equal to 0",
        )
 
    @classmethod
    def tearDownClass(cls):
        try:
            source_item = cls.feature_layer1_item.related_items("Service2Data", "forward")[0]
            if source_item:
                source_item.delete()
                cls.feature_layer1_item.delete()
        except IndexError as ie:
            cls.feature_layer1_item.delete()
            
        try:
            source_item2 = cls.feature_layer2_item.related_items("Service2Data", "forward")[0]
            if source_item2:
                source_item2.delete()
                cls.feature_layer2_item.delete()
        except IndexError as ie:
            cls.feature_layer2_item.delete()            

if __name__ == "__main__":
    unittest.main()
