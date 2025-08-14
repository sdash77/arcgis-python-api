import unittest
from arcgis.apps.storymap import StoryMap, Themes, Cover, Navigation, Image
from utils.decorators import integration_test, profiles
from integration.config import INTEGRATION_TEST_ITEM_TAG, get_resource_path


@integration_test
@profiles.enterprise_and_agol
class TestStoryMap(unittest.TestCase):
    """Test Basic Story Map Methods"""
    @classmethod
    def setUpClass(cls):
        # initiate storymap
        cls.story = StoryMap(gis=cls.gis)

        # image for story cover
        resource_path = get_resource_path("storymap")
        cls.river = Image(f'{resource_path}/storymap_image_river.jpg')

    def test_properties(self):
        """Assert properties"""
        assert self.story.content_list
        assert self.story.properties
        assert 'en' in self.story.story_locale
        assert isinstance(self.story.content_list[1], Navigation)
        assert isinstance(self.story.get("n-aTn8ak"), Cover)
        assert isinstance(self.story.navigation(hidden=True), list)

    def test_creating_and_saving(self):
        """Change cover/theme for the story"""
        # Edit story cover
        cover = self.story.content_list[0]
        cover.title = "My First Story"
        cover.summary = "Testing the Python API"
        cover.by_line = "Python Tester"
        cover.media = self.river

        # Change the story theme
        self.story.theme(Themes.SLATE)

        # Save the storymap changes
        assert self.story.save(tags=INTEGRATION_TEST_ITEM_TAG)

        assert self.story.content_list[0].title == "My First Story"
        assert self.story.get_theme() == Themes.SLATE.value

    @classmethod
    def tearDownClass(cls):
        cls.story.delete_story()


if __name__ == "__main__":
    unittest.main()
