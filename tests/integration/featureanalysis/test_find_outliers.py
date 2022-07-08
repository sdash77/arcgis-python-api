import unittest
import sys

# sys.path.insert(0, r"/Users/cowboy/GitHub/np_geo/src")
import datetime
from arcgis.features import FeatureLayer
from arcgis.gis import Item
from arcgis.gis import GIS
from arcgis.features.analyze_patterns import find_outliers
from config_tests import setup_profiles, stage_data

test_items = ["5183636f099c48789628226e5730fb13"]  # Traffic Collisions
profiles = ["online_test", "ent_test", "kube_test"]
setup_profiles(profiles[0], profiles[1], profiles[2])
stage_data(test_items)


class TestFindOutliers(unittest.TestCase):
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
            output_name = "overwrite_find_outliers_" + test_id
            print("Creating ", output_name)
            target_item = find_outliers(
                analysis_layer=traffic_lyr,
                shape_type="Fishnet",
                output_name=output_name,
            )

            # verify layer matches expected types
            assert isinstance(target_item, dict)
            target_lyr = target_item["outliers_result_layer"].layers[0]
            assert isinstance(target_lyr, FeatureLayer)

            # test overwriting first test
            print("Creating overwrite layer")
            overwrite = find_outliers(
                analysis_layer=traffic_lyr,
                shape_type="Hexagon",
                output_name=target_lyr,
                context={"overwrite": True},
            )
            assert isinstance(overwrite, dict)
            assert (
                target_item["outliers_result_layer"].id
                == overwrite["outliers_result_layer"].id
            )
            assert overwrite["outliers_result_layer"].delete()


if __name__ == "__main__":
    unittest.main()
