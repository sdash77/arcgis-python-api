import sys

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import datetime
import unittest
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.features.find_locations import derive_new_locations
from arcgis.gis import ProfileManager

profile_list = ProfileManager().list()

if not "ent11" in profile_list:
    GIS(
        url="https://gpportal.esri.com/portal/",
        username="admin",
        password="esri.agp",
        profile="ent11",
    )  # create enterprise 11 connection


profiles = ["your_online_profile", "ent11"]


class TestDeriveNewLocations(unittest.TestCase):
    def test_overwrite(self):
        """tests overwriting an Item layer using the context param"""
        for profile in profiles:
            # establish gis connection
            gis = GIS(profile=profile, verify_cert=False)
            print("User: ", gis.users.me.username)
            # gather layers
            if gis._is_agol:
                cougars_item = gis.content.get("747b24cdf0ef49acab79feb3dfcd4546")
            else:
                cougars_item = gis.content.get("8599c3fd627a4f818ea22be321e084f7")
            assert isinstance(cougars_item, Item)
            vegetation = cougars_item.layers[7]
            slope = cougars_item.layers[5]
            highways = cougars_item.layers[0]
            streams = cougars_item.layers[1]

            # create layer to be overwritten
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "overwrite_test_new_locations_" + test_id
            print("Creating ", output_name)
            target_item = derive_new_locations(
                input_layers=[slope, vegetation, streams, highways],
                expressions=[
                    {
                        "operator": "",
                        "layer": 0,
                        "selectingLayer": 1,
                        "spatialRel": "intersects",
                    }
                ],
                output_name=output_name,
            )
            assert isinstance(target_item, Item)
            target_layer = target_item.layers[0]
            assert isinstance(target_layer, FeatureLayer)
            target_layer_count_1 = len(target_item.layers)
            new_input_layers = [cougars_item.layers[1], cougars_item.layers[3]]

            # perform overwrite
            print("Creating overwrite layer")
            overwrite = derive_new_locations(
                input_layers=[vegetation, streams, highways],
                expressions=[
                    {
                        "operator": "",
                        "layer": 0,
                        "selectingLayer": 1,
                        "spatialRel": "intersects",
                    }
                ],
                output_name=target_layer,
                context={"overwrite": True},
            )
            assert isinstance(overwrite, Item)
            assert target_item.id == overwrite.id
            # only one layer results from overwrite
            assert len(target_item.layers) == target_layer_count_1
            # delete content created by story
            assert target_item.delete()


if __name__ == "__main__":
    unittest.main()
