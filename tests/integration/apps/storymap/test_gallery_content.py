import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Image, Gallery
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestGallery(unittest.TestCase):
    """Test Story Map Gallery content"""

    def test_create_swipe(self):
        gis = self.gis

        gallery = Gallery()

        assert gallery

        story = StoryMap(gis=gis)
        story.add(gallery)

        assert len(story.content_list) == 4
        assert isinstance(story.content_list[2], Gallery)

        story.delete_story()

    def add_content_to_gallery(self):
        gis = self.gis

        gallery = Gallery()

        assert gallery

        story = StoryMap(gis=gis)
        story.add(gallery)

        assert len(story.content_list) == 4
        assert isinstance(story.content_list[2], Gallery)

        # Construct items that will go into new slide
        im = Image(
            "https://www.nps.gov/npgallery/GetAsset/36106ED0-1DD8-B71C-07ED73544EA246C7/proxy/hires"
        )
        im2 = Image(
            "https://www.nps.gov/npgallery/GetAsset/36106ED0-1DD8-B71C-07ED73544EA246C7/proxy/hires"
        )

        gallery.add_images([im, im2])
        assert len(gallery.images) == 2

        story.delete_story()


if __name__ == "__main__":
    unittest.main()
