import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Image, Swipe
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestSwipe(unittest.TestCase):
    """Test Story Map Swipe content"""

    def test_create_swipe(self):
        gis = self.gis
        swipe = Swipe()

        assert swipe

        story = StoryMap(gis=gis)
        story.add(swipe)

        assert len(story.content_list) == 4
        assert isinstance(story.content_list[2], Swipe)

        story.delete_story()

    def add_content_to_swipe(self):
        gis = self.gis

        swipe = Swipe()

        assert swipe

        story = StoryMap(gis=gis)
        story.add(swipe)

        assert len(story.content_list) == 4
        assert isinstance(story.content_list[2], Swipe)

        # Construct items that will go into new slide
        im = Image(
            "https://www.nps.gov/npgallery/GetAsset/36106ED0-1DD8-B71C-07ED73544EA246C7/proxy/hires"
        )
        im2 = Image(
            "https://www.nps.gov/npgallery/GetAsset/36106ED0-1DD8-B71C-07ED73544EA246C7/proxy/hires"
        )

        swipe.edit(im, "left")
        swipe.edit(im2, "right")

        assert swipe.properties

        story.delete_story()


if __name__ == "__main__":
    unittest.main()
