import datetime
import unittest

from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer
from arcgis.features.use_proximity import create_buffers

profiles = ["your_online_profile", "your_enterprise_profile"]

class TestCreateBuffers(unittest.TestCase):
    def test_overwrite(self):
        """tests overwriting an Item layer using the context param"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            print('User: ', gis.users.me.username)
            offices_item = gis.content.get("1f163950afbb4bf39f3ee67cf411761d")
            assert isinstance(offices_item, Item)
            offices_layer = offices_item.layers[0]
            assert isinstance(offices_layer, FeatureLayer)
            test_id = str(datetime.datetime.now().microsecond)
            output_name = "overwrite_test_create_buffers_" + test_id
            print("Creating ", output_name)
            target_item = create_buffers(
                input_layer=offices_layer,
                distances=[100],
                output_name=output_name,
            )
            assert isinstance(target_item, Item)
            target_layer = target_item.layers[0]
            assert isinstance(target_layer, FeatureLayer)
            target_layer_count_1 = len(target_item.layers)
            overwrite = create_buffers(
                input_layer=offices_layer,
                distances = [150],
                output_name = target_layer,
                context={"overwrite": True},
            )
            assert isinstance(overwrite, Item)
            assert target_item.id == overwrite.id
            assert len(target_item.layers) == target_layer_count_1
            assert target_item.delete()
            break

if __name__ == "__main__":
    unittest.main()