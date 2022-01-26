import sys

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import datetime
import unittest
import pandas as pd
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.features.find_locations import find_existing_locations


profiles = ["your_online_profile", "ent11"]


class TestFindExistingLocation(unittest.TestCase):
    def test_overwrite(self):
        """tests overwriting an Item layer using the context param"""
        for profile in profiles:
            # establish gis connection
            gis = GIS(profile=profile, verify_cert=False)
            print("User: ", gis.users.me.username)

            # gather layers
            if gis._is_agol:
                cougar_item = gis.content.get("747b24cdf0ef49acab79feb3dfcd4546")
                stream_lyr = cougar_item.layers[6]
            else:
                cougar_item = gis.content.get("8599c3fd627a4f818ea22be321e084f7")
                stream_lyr = cougar_item.layers[1]
            assert isinstance(stream_lyr, FeatureLayer)

            # create layer that will be overwritten
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "test_find_existing_location_" + test_id
            print("Creating ", output_name)
            target_item = find_existing_locations(
                input_layers=[stream_lyr],
                expressions=[
                    {"operator": "", "layer": 0, "where": "ACRES > 1"},
                ],
                output_name=output_name,
            )
            assert isinstance(target_item, Item)
            target_layer = target_item.layers[0]
            assert isinstance(target_layer, FeatureLayer)

            # perform overwrite
            print("Overwriting target layer")
            overwrite = find_existing_locations(
                input_layers=[stream_lyr],
                expressions=[
                    {"operator": "", "layer": 0, "where": "ACRES > 1"},
                ],
                output_name=target_layer,
                context={"overwrite": True},
            )
            assert isinstance(overwrite, Item)
            assert target_item.id == overwrite.id
            # overwrite should not append. Only one layer should be present
            assert len(target_item.layers) == 1

            # delete items that were added for test purposes
            assert target_item.delete()


if __name__ == "__main__":
    unittest.main()
