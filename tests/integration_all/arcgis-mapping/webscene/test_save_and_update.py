from arcgis.features import FeatureLayer
from arcgis.gis import GIS, Item
from arcgis.map import Scene
from arcgis.map.renderers import SimpleRenderer
from arcgis.map.symbols import PolygonSymbol3D, Material, SolidEdges
import unittest
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestSaveAndUpdateMap(unittest.TestCase):
    def test_save_and_update(self):
        """Test saving a webmap, adding a layer, and then updating."""
        # create web scene
        wm = Scene(gis=self.gis)
        assert wm
        assert len(wm.content.layers) == 0

        # save, this creates a new item
        new_item = wm.save(
            {
                "title": "Scene Unit Test Save Scene",
                "snippet": "Test saving the webmap, adding a layer, and then updating it.",
                "tags": ["python", "webmap"],
            }
        )
        assert new_item
        assert isinstance(new_item, Item)

        # load new item into webmap class again
        new_wm = Scene(item=new_item, gis=self.gis)
        assert new_wm
        assert new_wm.item == new_item

        # add a layer
        layer = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        new_wm.content.add(
            layer,
            drawing_info={
                "renderer": SimpleRenderer(
                    symbol=PolygonSymbol3D(**{
                                "type": "PolygonSymbol3D",
                                "symbolLayers": [
                                    {
                                        "type": "Extrude",
                                        "material": Material(color= [255, 0, 0, 0.5]),
                                        "size": 100,
                                        "edges": SolidEdges(color= [50, 50, 50, 0.5]),
                                    }
                                ],
                            },)
                )
            }
        )
        assert len(new_wm.content.layers) == 1

        # update the map
        assert new_wm.update()

        # delete the item
        new_item.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
