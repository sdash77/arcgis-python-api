import unittest
from arcgis.gis import GIS, Item
from arcgis.apps.storymap import StoryMap, Themes
from arcgis.apps.storymap import (
    Image,
)
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestStoryMap(unittest.TestCase):
    """Test Basic Story Map Methods"""

    def test_editing(self):
        """Change the storycover for the story"""
        gis = self.gis
        story = StoryMap()

        # image for story cover
        river = Image(
            "https://www.nps.gov/npgallery/GetAsset/0022D3FF-1DD8-B71B-0BE3AD4C48F96FF9/proxy/hires"
        )

        # Edit story cover
        cover = story.content_list[0]
        cover.title = "My First Story"
        cover.summary = "Testing the Python API"
        cover.by_line = "Python Tester"
        cover.media = river
        cover.size = "large"
        cover.style = "transparent-with-light-color"
        cover.horizontal_alignment = "center"
        cover.vertical_alignment = "bottom"
        
        story.save()
        
        cover_data = story._properties["nodes"]["n-aTn8ak"]["data"]
        assert cover_data["title"] == "My First Story"
        assert cover_data["summary"] == "Testing the Python API"
        assert cover_data["byline"] == "Python Tester"
        assert cover_data["titlePanelSize"] == "large"
        assert cover_data["style"] == "transparent-with-light-color"
        assert cover_data["titlePanelHorizontalAlignment"] == "center"
        assert cover_data["titlePanelVerticalAlignment"] == "bottom"

        story.delete_story()


if __name__ == "__main__":
    unittest.main()
