from arcgis.map import Map
from arcgis.map.group_layer import GroupLayer
from arcgis.map.popups import PopupManager
import unittest
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestTablesMap(unittest.TestCase):
    def test_add_table(self):
        """Test getting, adding, and deleting bookmarks"""

        webmap = Map(gis=self.gis)
        assert webmap

        table_item = self.gis.content.get("9d9a0b8128f649029873e79900fa2885")
        
        #Test adding from tables property
        webmap.content.add(table_item.tables[0])
        
        assert len(webmap.content.tables) == 1
        assert len(webmap.content.layers) == 0
        
        #Test adding entire item
        webmap.content.add(table_item)
        assert len(webmap.content.tables) == 2
        assert len(webmap.content.layers) == 0

        #Test adding as a group
        layer_item = self.gis.content.get("bba3d0a070d34cea9a303c24a71d5190")
        items = [table_item.tables[0], layer_item.layers[0]]
        webmap.content.add(items)
        assert len(webmap.content.tables) == 2
        assert len(webmap.content.layers) == 1
        
        assert isinstance(webmap.content.layers[0], GroupLayer)
        group = webmap.content.layers[0]
        assert len(group.layers) == 2
        
    def test_table_popup(self):
        webmap = Map(gis=self.gis)
        assert webmap

        table_item = self.gis.content.get("9d9a0b8128f649029873e79900fa2885")
        
        #Test adding from tables property
        webmap.content.add(table_item.tables[0])
        
        pm = webmap.content.popup(0, is_table=True)
        assert isinstance(pm, PopupManager)
        
if __name__ == "__main__":
    unittest.main()
