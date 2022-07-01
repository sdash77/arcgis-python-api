import unittest
import sys

# sys.path.insert(0, r"/Users/cowboy/GitHub/np_geo/src")
import datetime
from arcgis.features import FeatureLayer
from arcgis.gis import Item
from arcgis.gis import GIS
from arcgis.features.analyze_patterns import find_point_clusters

profiles = ["online_test", "ent_test", "kube_test"]


class TestFindPointClusters(unittest.TestCase):
    def test_overwrite(self):
        # establish gis connection
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            print("User: ", gis.users.me.username)
            # gather layer
            traffic_item = gis.content.get("5183636f099c48789628226e5730fb13")
            assert isinstance(traffic_item, Item)
            traffic_lyr = traffic_item.layers[0]
            assert isinstance(traffic_lyr, FeatureLayer)

            # create layer that will be overwritten
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "overwrite_find_point_clusters_" + test_id
            print("Creating ", output_name)
            target_item = find_point_clusters(
                analysis_layer=traffic_lyr,
                min_features_cluster=50,
                output_name=output_name,
            )

            # verify layer matches expected types
            assert isinstance(target_item, Item)
            target_lyr = target_item.layers[0]
            assert isinstance(target_lyr, FeatureLayer)

            # test overwriting first test
            print("Creating overwrite layer")
            overwrite = find_point_clusters(
                analysis_layer=traffic_lyr,
                min_features_cluster=200,
                output_name=target_lyr,
                context={"overwrite": True},
            )
            assert isinstance(overwrite, Item)
            assert target_item.id == overwrite.id
            assert overwrite.delete()


if __name__ == "__main__":
    unittest.main()
