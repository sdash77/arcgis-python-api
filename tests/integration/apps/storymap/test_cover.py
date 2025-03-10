import sys
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
        story = StoryMap(gis=gis)

        # image for story cover
        river = Image(
            "https://www.nps.gov/npgallery/GetAsset/0022D3FF-1DD8-B71B-0BE3AD4C48F96FF9/proxy/hires"
        )

        # Edit story cover
        cover = story.content_list[0]
        cover.title = "My First Story"
        cover.summary = "Testing the Python API"
        cover.byline = "Python Tester"
        cover.media = river
        cover.type = "full"
        cover.size = "large"
        cover.style = "transparent-with-light-color"
        cover.horizontal_position = "center"
        cover.vertical_position = "bottom"
        
        story.save()
        
        cover_data = story._properties["nodes"]["n-aTn8ak"]["data"]
        assert cover_data["title"] == "My First Story"
        assert cover_data["summary"] == "Testing the Python API"
        assert cover_data["byline"] == "Python Tester"
        assert cover_data["titlePanelSize"] == "large"
        assert cover_data["titlePanelStyle"] == "transparent-with-light-color"
        assert cover_data["titlePanelHorizontalPosition"] == "center"
        assert cover_data["titlePanelVerticalPosition"] == "bottom"

        story._item.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
