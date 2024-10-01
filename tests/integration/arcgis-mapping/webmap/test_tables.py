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

        table_item = self.gis.content.advanced_search(
            '(car)  (typekeywords:Table)  -type:"Code Attachment" -type:"Featured Items" -type:"Symbol Set" -type:"Color Set" -type:"Windows Viewer Add In" -type:"Windows Viewer Configuration" -type:"Map Area" -typekeywords:"MapAreaPackage"'
        )["results"][0]
        
        #Test adding from tables property
        webmap.content.add(table_item.tables[0])
        
        assert len(webmap.content.tables) == 1
        assert len(webmap.content.layers) == 0
        
        #Test adding entire item
        webmap.content.add(table_item)
        assert len(webmap.content.tables) == 2
        assert len(webmap.content.layers) == 0
        
    def test_table_popup(self):
        webmap = Map(gis=self.gis)
        assert webmap

        table_item = self.gis.content.advanced_search(
            '(car)  (typekeywords:Table)  -type:"Code Attachment" -type:"Featured Items" -type:"Symbol Set" -type:"Color Set" -type:"Windows Viewer Add In" -type:"Windows Viewer Configuration" -type:"Map Area" -typekeywords:"MapAreaPackage"'
        )["results"][0]
        
        #Test adding from tables property
        webmap.content.add(table_item.tables[0])
        
        pm = webmap.content.popup(0, is_table=True)
        assert isinstance(pm, PopupManager)
        
if __name__ == "__main__":
    unittest.main()
