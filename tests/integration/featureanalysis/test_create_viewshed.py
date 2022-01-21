import datetime
import unittest

from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.features.find_locations import create_viewshed

profiles = ["your_online_profile", "your_enterprise_profile"]


class Test(unittest.TestCase):
    def test_overwrite(self):
        """tests overwriting an Item layer using the context param"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            print("User: ", gis.users.me.username)
            hq_item = gis.content.get("c7665d3c8e6f48a79f07b79677996bed")
            assert isinstance(hq_item, Item)
            hq_layer = hq_item.layers[0]
            assert isinstance(hq_layer, FeatureLayer)
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "overwrite_test_create_viewshed_" + test_id
            print("Creating ", output_name)
            target_item = create_viewshed(
                input_layer=hq_layer, output_name=output_name
            )
            assert isinstance(target_item, Item)
            target_layer = target_item.layers[0]
            assert isinstance(target_layer, FeatureLayer)
            target_layer_count_1 = len(target_item.layers)
            print("Creating overwrite layer")
            overwrite = create_viewshed(
                input_layer=hq_layer,
                maximum_distance=5,
                output_name=target_layer,
                context={"overwrite": True},
            )
            assert isinstance(overwrite, Item)
            assert target_item.id == overwrite.id
            assert len(target_item.layers) == target_layer_count_1
            assert target_item.delete()
            break


if __name__ == "__main__":
    unittest.main()
