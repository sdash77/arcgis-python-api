import datetime
import unittest
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.features.find_locations import create_watersheds
from .config_tests import setup_profiles, stage_data
from utils.decorators import integration_test

test_items = ["435fcf6cff1f4f34989e151c1f25d64a"]  # esri office
profiles = ["online_test", "ent_test", "kube_test"]
setup_profiles(profiles[0], profiles[1], profiles[2])
stage_data(test_items)

@integration_test
class TestCreateWatersheds(unittest.TestCase):
    def test_overwrite(self):
        """tests overwriting an Item layer using the context param"""
        for profile in profiles:
            # establish gis connection
            gis = GIS(profile=profile, verify_cert=False)
            print("User: ", gis.users.me.username)
            # gather layer
            office_item = gis.content.get("435fcf6cff1f4f34989e151c1f25d64a")
            assert isinstance(office_item, Item)
            office_lyr = office_item.layers[0]
            assert isinstance(office_lyr, FeatureLayer)

            # create layer that will be overwritten
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "overwrite_test_create_watersheds_" + test_id
            print("Creating ", output_name)
            target_item = create_watersheds(
                input_layer=office_lyr, output_name=output_name, context={"outSR": {"wkid": 4326}}
            )
            assert isinstance(target_item, Item)
            target_layer = target_item.layers[0]
            assert isinstance(target_layer, FeatureLayer)
            target_layer_count_1 = len(target_item.layers)

            # perform overwrite
            print("Creating overwrite layer")
            overwrite = create_watersheds(
                input_layer=office_lyr,
                source_database="90m",
                output_name=target_layer,
                context={"outSR": {"wkid": 4326}, "overwrite": True},
            )
            assert isinstance(overwrite, Item)
            assert target_item.id == overwrite.id
            # overwrite creates same number of layers. (In this case two)
            assert len(target_item.layers) == target_layer_count_1
            # delete content created by tests
            assert target_item.delete()


if __name__ == "__main__":
    unittest.main()
