import datetime
import unittest

from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.features.analysis import aggregate_points

profiles = ["your_online_profile", "your_enterprise_profile"]


class TestAggregatePoints(unittest.TestCase):
    def test_overwrite(self):
        """tests overwriting an Item layer using the context param"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            print("User: ", gis.users.me.username)
            point_item = gis.content.get("1923d4e74ac947dab4f8c94d2c2a7a9c")
            polygon_item = gis.content.get("78778fe9e4244f71b8194122d1f228ae")
            assert isinstance(point_item, Item)
            assert isinstance(polygon_item, Item)
            point_layer = point_item.layers[0]
            polygon_layer = polygon_item.layers[3]
            assert isinstance(point_layer, FeatureLayer)
            assert isinstance(polygon_layer, FeatureLayer)
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "overwrite_test_agg_" + test_id
            target_item = aggregate_points(
                point_layer=point_layer,
                polygon_layer=polygon_layer,
                keep_boundaries_with_no_points=False,
                output_name=output_name,
            )
            assert isinstance(target_item, Item)
            target_layer = target_item.layers[0]
            new_polygon_layer = polygon_item.layers[1]
            assert isinstance(target_layer, FeatureLayer)
            assert isinstance(new_polygon_layer, FeatureLayer)
            overwrite = aggregate_points(
                point_layer=point_layer,
                polygon_layer=new_polygon_layer,
                keep_boundaries_with_no_points=False,
                output_name=target_layer,
                context={"overwrite": True},
            )
            assert isinstance(overwrite, Item)
            assert target_item.id == overwrite.id
            assert len(target_item.layers) == 1
            assert target_item.delete()
            break


if __name__ == "__main__":
    unittest.main()
