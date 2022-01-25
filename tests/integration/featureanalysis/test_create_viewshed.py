import unittest
import datetime
import sys

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.features.find_locations import create_viewshed

profiles = ["your_online_profile", "ent11"]


class Test(unittest.TestCase):
    def test_overwrite(self):
        """tests overwriting an Item layer using the context param"""
        for profile in profiles:
            # establish gis connection
            gis = GIS(profile=profile, verify_cert=False)
            print("User: ", gis.users.me.username)
            # gather layers
            if gis._is_agol:
                hq_item = gis.content.get("c7665d3c8e6f48a79f07b79677996bed")
            else:
                hq_item = gis.content.get("a02718d5e01b44439721be7c5d6cf2b2")
            assert isinstance(hq_item, Item)
            hq_lyr = hq_item.layers[0]
            assert isinstance(hq_lyr, FeatureLayer)

            # create layer that will be overwritten
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "overwrite_test_create_viewshed_" + test_id
            print("Creating ", output_name)
            target_item = create_viewshed(input_layer=hq_lyr, output_name=output_name)
            assert isinstance(target_item, Item)
            target_layer = target_item.layers[0]
            assert isinstance(target_layer, FeatureLayer)
            target_layer_count_1 = len(target_item.layers)

            # perform overwrite
            print("Creating overwrite layer")
            overwrite = create_viewshed(
                input_layer=hq_lyr,
                maximum_distance=5,
                output_name=target_layer,
                context={"overwrite": True},
            )
            assert isinstance(overwrite, Item)
            assert target_item.id == overwrite.id
            # overwrite only produces one layer
            assert len(target_item.layers) == target_layer_count_1
            # deleted content created by test
            assert target_item.delete()


if __name__ == "__main__":
    unittest.main()
