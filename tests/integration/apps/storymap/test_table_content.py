import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Table, Text
from utils.decorators import integration_test

profiles = ["your_online_profile", "your_enterprise_profile"]


@integration_test
class TestTableContent(unittest.TestCase):
    """Test adding a table and editing"""

    def test_add_table(self):
        """Test adding Table and seeing properties"""
        for profile in profiles:
            with self.subTest(msg=profile):
                # establish gis connection
                gis = GIS(profile=profile, verify_cert=False)
                story = StoryMap()
                table = Table(3, 3)
                story.add(table)

                assert table
                assert isinstance(story.content_list[2], Table)

                cells = table.content
                cells.loc["0"] = [
                    {"value": Text("Hello")},
                    {"value": Text("World")},
                    {"value": Text("!")},
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

                item = gis.content.get(story._itemid)
                assert item.delete()


if __name__ == "__main__":
    unittest.main()
