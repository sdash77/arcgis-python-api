from arcgis.map import Map
from arcgis.map.popups import PopupManager
import unittest
import os
from utils.decorators import integration_test, profiles
from integration.config import get_resource_path

@profiles.agol
@integration_test
class TestTablesMap(unittest.TestCase):
    # setup class by publishing csv data as table to AGOL
    @classmethod
    def setUpClass(cls):
        content = cls.gis.content
        cls.csv_path = get_resource_path("/mapping/capitals_tbl.csv")
        cls.table_item_file = content.add({}, data=cls.csv_path)  # add the file
        publish_parameters = content.analyze(
            item=cls.table_item_file, file_type="csv", location_type="none"
        )["publishParameters"]
        publish_parameters["name"] = "capitals_tbl_test"
        cls.table_item = cls.table_item_file.publish(
            publish_parameters=publish_parameters
        )

    def test_add_table(self):
        """Test getting and adding table to map"""

        webmap = Map(gis=self.gis)
        assert webmap

        # Test adding from tables property
        webmap.content.add(self.table_item.tables[0])

        assert len(webmap.content.tables) == 1
        assert len(webmap.content.layers) == 0

        # Test adding entire item
        webmap.content.add(self.table_item)
        assert len(webmap.content.tables) == 2
        assert len(webmap.content.layers) == 0

    def test_table_popup(self):
        """Test getting popup manager for a table on a map"""
        webmap = Map(gis=self.gis)
        assert webmap

        # Test adding from tables property
        webmap.content.add(self.table_item.tables[0])

        pm = webmap.content.popup(0, is_table=True)
        assert isinstance(pm, PopupManager)

    # cleanup by deleting the table item
    @classmethod
    def tearDownClass(cls):
        cls.gis.content.delete_items(
            [cls.table_item, cls.table_item_file], permanent=True
        )


if __name__ == "__main__":
    unittest.main()
