import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Image, Gallery
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestImageContent(unittest.TestCase):
    """Test adding an Image and seeing properties"""

    def test_add_image(self):
        """test adding an image to a story"""

        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)
        img = Image(
            "https://www.nps.gov/npgallery/GetAsset/69680c29-caa3-42da-93d9-32925e9ed409/proxy/hires"
        )
        image = story.add(img, "Trees with a deer", "Sequoia trees in the distance")
        story.add()  # separator

        assert image
        assert img.properties
        assert img.caption
        assert img.alt_text
        
        # set link
        img.link = "www.google.com"
        assert img.link == "www.google.com"
        
        img.full_view = True
        assert img.full_view == True
        
        item = gis.content.get(story._itemid)
        assert story.delete_story()

    def test_create_gallery(self):
        """Test creating a gallery and adding images to it"""
        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)
        gallery = Gallery()
        assert gallery

        story.add(gallery)
        assert gallery.properties

        # Create Images to add to gallery
        i1 = Image(
            "https://www.nps.gov/npgallery/GetAsset/003805FB-155D-451F-6760BEF19A9F5039/proxy/hires"
        )
        i2 = Image(
            "https://www.nps.gov/npgallery/GetAsset/002E571C-155D-451F-6729E4B9B3830C6A/proxy/hires"
        )
        i3 = Image(
            "https://www.nps.gov/npgallery/GetAsset/003BA5FF-155D-451F-678D49A2F0585330/proxy/hires"
        )
        i4 = Image(
            "https://www.nps.gov/npgallery/GetAsset/00450151-155D-451F-67AF679D111DAD36/proxy/hires"
        )

        gallery.add_images([i1, i2, i3, i4])
        print(gallery.images)
        assert gallery.images

        item = gis.content.get(story._itemid)
        assert story.delete_story()


if __name__ == "__main__":
    unittest.main()
