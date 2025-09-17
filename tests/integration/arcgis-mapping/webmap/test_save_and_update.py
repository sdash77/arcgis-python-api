from arcgis.features import FeatureLayer
from arcgis.gis import Item
from arcgis.map import Map
import unittest
from utils.decorators import integration_test, profiles


@profiles.enterprise_and_agol
@integration_test
class TestSaveAndUpdateMap(unittest.TestCase):
    def test_save_and_update(self):
        """Test saving a webmap, adding a layer, and then updating."""
        # create webmap
        wm = Map(gis=self.gis)
        assert wm
        assert len(wm.content.layers) == 0

        # save, this creates a new item
        new_item = wm.save(
            {
                "title": "Map Unit Test Save Map",
                "snippet": "Test saving the webmap, adding a layer, and then updating it.",
                "tags": ["python", "web_map"],
            }
        )

        assert new_item
        assert isinstance(new_item, Item)

        # load new item into webmap class again
        new_wm = Map(item=new_item, gis=self.gis)
        assert new_wm
        assert new_wm.item == new_item

        # add a layer
        layer = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        new_wm.content.add(layer)
        assert len(new_wm.content.layers) == 1

        # update the map
        assert new_wm.update(
            item_properties={"tags": new_wm.item.tags + ["updated_tag"]}
        )
        assert len(new_wm.item.tags) == 3

        # delete the item
        new_item.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
