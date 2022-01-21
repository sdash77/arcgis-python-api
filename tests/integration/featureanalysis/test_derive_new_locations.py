import datetime
import unittest

from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.features.find_locations import derive_new_locations

profiles = ["your_online_profile", "your_enterprise_profile"]

class Test(unittest.TestCase):
    def test_overwrite(self):
        """tests overwriting an Item layer using the context param"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            print('User: ', gis.users.me.username)
            cougars_item = gis.content.get("af91a19a8c054e07b77976a3745c9bb6")
            assert isinstance(cougars_item, Item)
            input_layers = [
                cougars_item.layers[2],
                cougars_item.layers[1],
                cougars_item.layers[5],
                cougars_item.layers[4]
            ]
            for cougar_layer in input_layers:
                assert isinstance(cougar_layer, FeatureLayer)
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "overwrite_test_new_locations_" + test_id
            print("Creating ", output_name)
            target_item = derive_new_locations(
                input_layers=input_layers, output_name=output_name
            )
            assert isinstance(target_item, Item)
            target_layer = target_item.layers[0]
            assert isinstance(target_layer, FeatureLayer)
            target_layer_count_1 = len(target_item.layers)
            new_input_layers = [
                cougars_item.layers[2],
                cougars_item.layers[1],
                cougars_item.layers[5],
                cougars_item.layers[3]
            ]
            print("Creating overwrite layer")
            overwrite = derive_new_locations(
                input_layers=new_input_layers,
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