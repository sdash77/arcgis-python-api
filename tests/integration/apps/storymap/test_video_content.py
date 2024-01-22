# import sys
# sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Video
from utils.decorators import integration_test

profiles = ["your_online_profile", "your_enterprise_profile"]


@integration_test
class TestVideoContent(unittest.TestCase):
    """Test adding an video and seeing properties"""

    def test_add_video(self):
        """Test adding a Video and seeing properties"""
        for profile in profiles:
            with self.subTest(msg=profile):
                # establish gis connection
                gis = GIS(profile=profile, verify_cert=False)
                story = StoryMap()
                vid = Video("https://www.youtube.com/embed/8wY14zHDmEs")
                video = story.add(vid)

                assert video
                assert vid.video

                item = gis.content.get(story._itemid)
                assert item.delete()

    def test_replace_url(self):
        for profile in profiles:
            with self.subTest(msg=profile):
                # establish gis connection
                gis = GIS(profile=profile, verify_cert=False)
                story = StoryMap()
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
                assert item.delete()


if __name__ == "__main__":
    unittest.main()
