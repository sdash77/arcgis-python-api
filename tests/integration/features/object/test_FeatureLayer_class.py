import os
import unittest
from arcgis.gis import GIS, Item, features, ItemProperties
from arcgis.features import FeatureLayer, FeatureLayerCollection, FeatureSet, Feature
from pandas import DataFrame
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test, profiles


@profiles.devext
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
        csv_path = os.path.join(cls.qalab_cls_path, "edit_features_points.csv")
        cls.feature_layer_item = cls.publish_test_item(cls.gis, layer_name, csv_path)
        cls.assertIsNotNone(
            cls.feature_layer_item, f"Error publishing test item: {layer_name}"
        )
        # Publish feature layer for delete_features if it does not exist
        layer_name_delfeatures = cls.namePrefix + "delfeatures"
        fgdb_path = os.path.join(
            cls.qalab_cls_path, "set1_fortune10_delfeatures.gdb.zip"
        )
        cls.feature_layer_del_features = cls.publish_test_item(
            cls.gis, layer_name_delfeatures, fgdb_path
        )
        cls.assertIsNotNone(
            cls.feature_layer_del_features,
            f"Error publishing test item: {layer_name_delfeatures}",
        )

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
    def publish_test_item(cls, gis: GIS, layer_name: str, source_data_path: str):
        source_item = None
        # Clean out existing items
        item_types = ["CSV", "File Geodatabase", "Feature Layer"]
        for itm_type in item_types:
            search_result = gis.content.search(layer_name, item_type=itm_type)
            for search_item in search_result:
                search_item.delete(permanent=True)
        try:
            item_type = (
                "CSV" if source_data_path[-3:].upper() == "CSV" else "File Geodatabase"
            )
            ip = ItemProperties(
                title=layer_name,
                item_type=item_type,
                tags=["ntgrtn-tst"],
                snippet="Item for Feature Layer integration testing",
            )
            root_folder = gis.content.folders.get()
            source_item = root_folder.add(
                item_properties=ip,
                file=source_data_path,
            ).result()
            # publish the item
            if source_item:
                feature_layer_item = source_item.publish(
                    {"name": layer_name, "tags": "ntgrtn-tst"}
                )
                if feature_layer_item is not None:
                    print("Published edit_feature_definition_points feature layer")
                    is_prepped_for_editing = cls.prep_test_item(feature_layer_item)
                    if is_prepped_for_editing:
                        return feature_layer_item
                    else:
                        raise Exception("Could not update editing capabilities")
        except Exception as ex:
            if source_item:
                source_item.delete(permanent=True)
            raise Exception("Failed to add necessary item file to portal.", ex)

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

    @classmethod
    def tearDownClass(cls):
        try:
            source_item = cls.feature_layer_item.related_items(
                "Service2Data", "forward"
            )[0]
            if source_item:
                source_item.delete(permanent=True)
                cls.feature_layer_item.delete(permanent=True)
        except IndexError as ie:
            cls.feature_layer_item.delete(permanent=True)

        try:
            source_item2 = cls.feature_layer_del_features.related_items(
                "Service2Data", "forward"
            )[0]
            if source_item2:
                source_item2.delete()
                cls.feature_layer_del_features.delete(permanent=True)
        except IndexError as ie:
            cls.feature_layer_del_features.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
