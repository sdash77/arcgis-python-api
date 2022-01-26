import sys

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import datetime
import unittest
import pandas as pd
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.features.summarize_data import summarize_nearby

profiles = ["your_online_profile", "ent11"]


class TestSummarizeNearby(unittest.TestCase):
    def test_overwrite(self):
        """tests overwriting an Item layer using the context param"""
        for profile in profiles:
            # establish gis connection
            gis = GIS(profile=profile, verify_cert=False)
            print("User: ", gis.users.me.username)
            if gis._is_agol:
                hq_item = gis.content.get("c7665d3c8e6f48a79f07b79677996bed")
                office_item = gis.content.get("b96b5740372b4b838d621716264bb21d")
            else:
                hq_item = gis.content.get("a02718d5e01b44439721be7c5d6cf2b2")
                office_item = gis.content.get("999b3776bdae41acb787ae0ce2dfce0e")
            assert isinstance(hq_item, Item)
            assert isinstance(office_item, Item)
            hq_lyr = hq_item.layers[0]
            office_lyr = office_item.layers[0]
            assert isinstance(hq_lyr, FeatureLayer)
            assert isinstance(office_lyr, FeatureLayer)

            # create layer that will be overwritten
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "test_summarize_nearby_" + test_id
            print("Creating ", output_name)
            target_item = summarize_nearby(
                sum_nearby_layer=hq_lyr,
                summary_layer=office_lyr,
                near_type="StraightLine",
                distances=[5],
                units="Miles",
                time_zone_for_time_of_day="GeoLocal",
                return_boundaries=False,
                sum_shape=True,
                shape_units=None,
                output_name=output_name,
            )
            assert isinstance(target_item, Item)
            target_layer = target_item.layers[0]
            assert isinstance(target_layer, FeatureLayer)

            # perform overwrite
            print("Overwriting target layer")
            overwrite = summarize_nearby(
                sum_nearby_layer=hq_lyr,
                summary_layer=office_lyr,
                near_type="StraightLine",
                distances=[5],
                units="Miles",
                time_zone_for_time_of_day="GeoLocal",
                return_boundaries=False,
                sum_shape=True,
                shape_units=None,
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
