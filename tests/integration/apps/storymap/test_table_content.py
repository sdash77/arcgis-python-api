import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Table, Text
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestTableContent(unittest.TestCase):
    """Test adding a table and editing"""

    def test_add_table(self):
        """Test adding Table and seeing properties"""
        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)
        table = Table(3, 3)
        story.add(table)

        assert table
        assert isinstance(story.content_list[2], Table)

        cells = table.content
        cells.loc["0"] = [
            {"value": "Hello"},
            {"value": Text("World")},
            {"value": "!"},
        ]
        cells.loc["1"] = [
            {"value": Text("Hello")},
            {"value": Text("World")},
            {"value": Text("!")},
        ]
        cells.loc["2"] = [
            {"value": Text("Hello")},
            {"value": Text("World")},
            {"value": Text("!")},
        ]

        table.content = cells

        story.save()
        item = gis.content.get(story._itemid)
        assert item
        assert story.delete_story()


if __name__ == "__main__":
    unittest.main()
