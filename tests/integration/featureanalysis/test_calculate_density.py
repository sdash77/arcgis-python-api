import datetime
import unittest

from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.features.analyze_patterns import calculate_density

profiles = ["your_online_profile", "your_enterprise_profile"]


class TestCalculateDensity(unittest.TestCase):
    def test_overwrite(self):
        """tests overwriting an Item layer using the context param"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            print("User: ", gis.users.me.username)
            point_item = gis.content.get("79d3e458dcaf486f81c5591a67538179")
            polygon_item = gis.content.get("17339081d410464a94d2df1ddd95d3d6")
            assert isinstance(point_item, Item)
            assert isinstance(polygon_item, Item)
            point_layer = point_item.layers[0]
            polygon_layer = polygon_item.layers[0]
            assert isinstance(point_layer, FeatureLayer)
            assert isinstance(polygon_layer, FeatureLayer)
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "overwrite_test_calc_density_" + test_id
            print("Creating ", output_name)
            target_item = calculate_density(
                input_layer=point_layer, output_name=output_name
            )
            assert isinstance(target_item, Item)
            target_layer = target_item.layers[0]
            assert isinstance(target_layer, FeatureLayer)
            print("Overwriting target layer")
            overwrite = calculate_density(
                input_layer=point_layer,
                bounding_polygon_layer=polygon_layer,
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
