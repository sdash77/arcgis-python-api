import sys

sys.path.insert(0, r"C:\workspace\Geosaurus_MapWidget")
sys.path.insert(0, r"C:\workspace\geosaurus\src")
from arcgis.features import FeatureLayer
from arcgis.gis import GIS, Item
from arcgis.map import Map
import unittest

PROFILES = ["your_online_profile"]


class TestSaveAndUpdateMap(unittest.TestCase):
    def test_save_and_update(self):
        """Test saving a webmap, adding a layer, and then updating."""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Map(gis=gis)
            assert wm
            assert len(wm.content.layers) == 0

            # save, this creates a new item
            new_item = wm.save(
                {
                    "title": "Map Unit Test Save Map",
                    "snippet": "Test saving the webmap, adding a layer, and then updating it.",
                    "tags": ["python", "webmap"],
                }
            )
            assert new_item
            assert isinstance(new_item, Item)

            # load new item into webmap class again
            new_wm = Map(item=new_item, gis=gis)
            assert new_wm
            assert new_wm.item == new_item

            # add a layer
            layer = FeatureLayer(
                "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
            )
            new_wm.content.add(layer)
            assert len(new_wm.content.layers) == 1

            # update the map
            assert new_wm.update()

            # delete the item
            new_item.delete()


if __name__ == "__main__":
    unittest.main()
