import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestStoryMapsCopyContent(unittest.TestCase):
    """This test is built to test the copy content method on the arcgis storymap"""

    def test_copy_content(self):
        """tests copying content to a new story map"""
        # establish gis connection
        gis = self.gis
        if gis._is_agol:
            sm = StoryMap("ad5362af097845598a47f034c4096e2a")
            # get the Text, Map, Image, and Swipe nodes that will be copied
            nodes_to_copy = ["n-ByaApK", "n-6UzYoJ", "n-bOzGMy", "n-yPjEV5"]
        else:
            sm = StoryMap("bbca7674b8bc4fa9ab12d8b66e4a7467")
            # get the Text, Map, Image, and Swipe nodes that will be copied
            nodes_to_copy = ["n-VPFcjj", "n-Cyskj8", "n-HzZGw2", "n-4ih3Ig"]
        assert sm.content_list

        # create new story
        target_story = StoryMap(gis=gis)
        assert target_story

        # copy content over
        sm.copy_content(target_story=target_story, node_list=nodes_to_copy)

        # make sure copy occurred:
        assert len(target_story.content_list) == 7

        # put a breakpoint after this if you want to see the story printed
        target_story.save()

        # delete target story
        target_story.delete_story()


if __name__ == "__main__":
    unittest.main()
