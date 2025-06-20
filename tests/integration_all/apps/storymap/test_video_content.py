import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Video
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestVideoContent(unittest.TestCase):
    """Test adding an video and seeing properties"""

    def test_add_video(self):
        """Test adding a Video and seeing properties"""
        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)
        vid = Video("https://www.youtube.com/embed/8wY14zHDmEs")
        video = story.add(vid)

        assert video
        assert vid.video

        item = gis.content.get(story._itemid)
        assert story.delete_story()

    def test_replace_url(self):
        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)
        vid = Video("https://www.youtube.com/embed/8wY14zHDmEs")
        video = story.add(vid)

        new_video = "https://www.youtube.com/embed/G6b7Kgvd0iA"
        print(vid.video)

        vid.caption = "This is now a url"
        vid.video = new_video
        print(vid.video)
        print(vid.caption)

        assert vid.properties
        assert vid._is_url

        item = gis.content.get(story._itemid)
        assert story.delete_story()


if __name__ == "__main__":
    unittest.main()
