import os
import uuid
import unittest
from arcgis.features import FeatureLayer, FeatureLayerCollection, FeatureSet, Feature
from arcgis.gis._impl._dataclasses._contentds import ItemTypeEnum

from pandas import DataFrame
from integration.config import QALAB_ROOT_PATH, get_resource_path
from utils.decorators import integration_test, profiles
from utils.data_utils import publish_test_item, cleanup_published_items
from integration.config import get_resource_path


@profiles.enterprise_and_agol
@integration_test
class TestFeatureLayerClass(unittest.TestCase):
    """
    Test to check if a FeatureLayer object works with builtin portal and agol
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        Publish test Items
        :return:
        """

        # Publish feature layer
        layer_name = f"dino_FeatureLayer_basic_{uuid.uuid4().hex[:6]}"
        csv_path = get_resource_path(
            "staging_data/feature_object/feature_layer_class/edit_features_points.csv",
            unique_copy=True,
        )
        capabilities = {"capabilities": "Query,Uploads,Editing,Create,Update,Delete"}
        cls.feature_layer_item = publish_test_item(
            cls.gis,
            layer_name,
            csv_path,
            ItemTypeEnum.CSV,
            override_capabilities=capabilities,
        )
        assert cls.feature_layer_item, "Feature layer item not found"
        assert (
            len(cls.feature_layer_item.layers) > 0
        ), f"No layers found in collection: {layer_name}"

        # Publish feature layer
        layer_name_delfeatures = f"dino_FeatureLayer_delfeatures_{uuid.uuid4().hex[:6]}"
        fgdb_path = get_resource_path(
            "staging_data/feature_object/feature_layer_class/set1_fortune10_delfeatures.gdb.zip",
            unique_copy=True,
        )
        cls.feature_layer_del_features = publish_test_item(
            cls.gis, layer_name_delfeatures, fgdb_path, ItemTypeEnum.FILE_GEODATABASE
        )
        assert (
            cls.feature_layer_del_features
        ), f"Error publishing test item: {layer_name_delfeatures}"
        assert (
            len(cls.feature_layer_del_features.layers) > 0
        ), f"No layers found in collection: {layer_name_delfeatures}"

    def test_feature_mod_classes(self):
        """
        Purpose of this test is to obtain main objects in feature module and verify their types are correct.
        :return:
        """
        # check Item.layers property yields a list of FeatureLayer objects
        flayers = self.feature_layer_item.layers
        assert isinstance(flayers, list)
        assert isinstance(flayers[0], FeatureLayer)

        # check a FeatureLayerCollection object can be created from Item object thru fromitem()
        flc = FeatureLayerCollection.fromitem(self.feature_layer_item)
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
        flayer0 = self.feature_layer_item.layers[0]
        fset = self.feature_layer_item.layers[0].query("city_ID=1")
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
        flayer0 = self.feature_layer_item.layers[0]
        county_fs_df = flayer0.query(as_df=True)
        assert isinstance(county_fs_df, DataFrame)
        self.assertEqual(5, county_fs_df.shape[0], "Number of features not correct")

    def test_delete_features(self):
        """
        test for deleting features with edit_features()
        """
        # access the feature layer and its feature for editing
        flayer0 = self.feature_layer_del_features.layers[0]

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
        cleanup_published_items(
            [cls.feature_layer_item, cls.feature_layer_del_features]
        )


if __name__ == "__main__":
    unittest.main()
