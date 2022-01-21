import datetime
import unittest

from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.features.find_locations import choose_best_facilities

profiles = ["your_online_profile", "your_enterprise_profile"]


class TestChooseBestFacilities(unittest.TestCase):
    def test_overwrite(self):
        """tests overwriting an Item layer using the context param"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            print("User: ", gis.users.me.username)
            offices_item = gis.content.get("1f163950afbb4bf39f3ee67cf411761d")
            hq_item = gis.content.get("c7665d3c8e6f48a79f07b79677996bed")
            assert isinstance(offices_item, Item)
            assert isinstance(hq_item, Item)
            offices_layer = offices_item.layers[0]
            hq_layer = hq_item.layers[0]
            assert isinstance(offices_layer, FeatureLayer)
            assert isinstance(hq_layer, FeatureLayer)
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "overwrite_test_best_facilities_" + test_id
            print("Creating ", output_name)
            target_item = choose_best_facilities(
                demand_locations_layer=offices_layer,
                max_travel_range=30,
                travel_mode="Driving Time",
                required_facilities_layer=hq_layer,
                output_name=output_name,
            )
            assert isinstance(target_item, Item)
            target_layer = target_item.layers[0]
            assert isinstance(target_layer, FeatureLayer)
            target_layer_count_1 = len(target_item.layers)
            overwrite = choose_best_facilities(
                demand_locations_layer=offices_layer,
                max_travel_range=45,
                travel_mode="Driving Time",
                required_facilities_layer=hq_layer,
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
