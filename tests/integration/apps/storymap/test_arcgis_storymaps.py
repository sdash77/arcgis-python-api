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

    def test_creating_and_saving(self):
        """Change the storycover for the story"""
        gis = self.gis
        story = StoryMap()

        # assert some properties
        assert story.nodes
        assert story.properties
        assert story.cover_date
        assert story.story_locale
        assert isinstance(story.navigation_list, list)
        assert story.get("n-aTn8ak")

        assert isinstance(story.navigation(hidden=True), list)

        # image for story cover
        river = Image(
            "https://www.nps.gov/npgallery/GetAsset/0022D3FF-1DD8-B71B-0BE3AD4C48F96FF9/proxy/hires"
        )

        # Edit story cover
        cover = story.content[0]
        cover.title = "My First Story"
        cover.summary = "Testing the Python API"
        cover.by_line = "Python Tester"
        cover.media = river
        assert story.cover_date
        assert story.nodes

        """Change the story theme"""
        story.theme(Themes.SLATE)
        assert story.get_theme() == Themes.SLATE.value
        assert story.properties

        assert story.save()

        story.delete_story()


if __name__ == "__main__":
    unittest.main()
