import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Embed, Image, Sidecar, Text
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestSideCar(unittest.TestCase):
    """Test Story Map Sidecar content"""

    def test_create_sidecar(self):
        print("Testing create")
        gis = self.gis

        sidecar = Sidecar("floating-panel")

        assert sidecar

        story = StoryMap(gis=gis)
        story.add(sidecar)

        assert len(story.content_list) == 4
        assert isinstance(story.content_list[2], Sidecar)

        story.delete_story()

    def add_content_to_sidecar(self):
        print("Testing adding")
        gis = self.gis

        sidecar = Sidecar("floating-panel")

        assert sidecar

        story = StoryMap(gis=gis)
        story.add(sidecar)

        assert len(story.content_list) == 4
        assert isinstance(story.content_list[2], Sidecar)

        # Construct items that will go into new slide
        im = Image(
            "https://www.nps.gov/npgallery/GetAsset/36106ED0-1DD8-B71C-07ED73544EA246C7/proxy/hires"
        )
        txt = Text("This is a grizzly bear.")
        txt2 = Text("They can be found in some of our national parks.")
        link = Embed(
            "https://www.nwf.org/Educational-Resources/Wildlife-Guide/Mammals/Grizzly-Bear"
        )

        # Create list for narrative panel content
        nar_pan = [txt, txt2, link]

        # Add slide to sidecar with the content
        new_slide = sidecar.add_slide(nar_pan, im, None)
        assert new_slide
        assert len(sidecar._slides) == 1

        # remove the slide
        sidecar.remove_slide(new_slide["New Slide"])
        assert len(sidecar._slides) == 0

        story.delete_story()


if __name__ == "__main__":
    unittest.main()
