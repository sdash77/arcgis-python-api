import unittest
import datetime
from arcgis.gis import Item
from arcgis.gis import GIS
from arcgis.features.manage_data import create_route_layers
from config_tests import setup_profiles, stage_data
from utils.decorators import integration_test

test_items = ["3793ab5f2baa47919bd4212b3d0f08e2"]  # LA Route Geodatabase
profiles = ["online_test", "ent_test", "kube_test"]
setup_profiles(
    profiles[0],
    profiles[1],
    profiles[2],
)
stage_data(test_items)


@integration_test
class TestCreateRouteLayers(unittest.TestCase):
    def test_routing(self):
        # establish gis connection
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            print("User: ", gis.users.me.username)
            # gather layer
            stops_item = gis.content.get("3793ab5f2baa47919bd4212b3d0f08e2")
            assert isinstance(stops_item, Item)

            # create layer that will be overwritten
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "test_create_route_layers_" + test_id
            print("Creating ", output_name)
            target_item = create_route_layers(
                route_data_item=stops_item,
                delete_route_data_item=False,
                tags="test",
                summary="check",
                route_name_prefix="test",
            )

            # verify types and deletion are as expected
            assert isinstance(target_item, list)
            for route in target_item:
                assert isinstance(route, Item)
                assert route.delete()


if __name__ == "__main__":
    unittest.main()
