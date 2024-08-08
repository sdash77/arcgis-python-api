import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Embed, Image, Sidecar, Text, Map
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

    def test_add_action_viewpoint(self):
        print("Testing add action viewpoint")
        gis = self.gis

        sidecar = Sidecar("floating-panel")

        assert sidecar

        story = StoryMap(gis=gis)
        story.add(sidecar)

        assert len(story.content_list) == 4
        assert isinstance(story.content_list[2], Sidecar)

        # Construct items that will go into new slide
        mmap = Map(item=gis.content.get("f47a5a35be8c41f7890c1763f65a6d9f"))
        txt = Text("This is a grizzly bear.")
        txt2 = Text("They can be found in some of our national parks.")
        link = Embed(
            "https://www.nwf.org/Educational-Resources/Wildlife-Guide/Mammals/Grizzly-Bear"
        )

        # Create list for narrative panel content
        nar_pan = [txt, txt2, link]

        # Add slide to sidecar with the content
        new_slide = sidecar.add_slide(nar_pan, mmap, None)
        assert new_slide
        assert len(sidecar._slides) == 1

        # Add action viewpoint to the slide
        vp = {
            "scale": 100000,
            "target": [-122.45, 37.75],
            "heading": 180,
            "tilt": 60,
        }
        sidecar.add_action(1, viewpoint=vp)

        story.delete_story()
    
    def test_add_action_media(self):
        print("Testing add action media")
        gis = self.gis

        sidecar = Sidecar("floating-panel")

        assert sidecar

        story = StoryMap(gis=gis)
        story.add(sidecar)

        assert len(story.content_list) == 4
        assert isinstance(story.content_list[2], Sidecar)

        # Construct items that will go into new slide
        mmap = Map(item=gis.content.get("f47a5a35be8c41f7890c1763f65a6d9f"))
        txt = Text("This is a grizzly bear.")
        txt2 = Text("They can be found in some of our national parks.")
        link = Embed(
            "https://www.nwf.org/Educational-Resources/Wildlife-Guide/Mammals/Grizzly-Bear"
        )

        # Create list for narrative panel content
        nar_pan = [txt, txt2, link]

        # Add slide to sidecar with the content
        new_slide = sidecar.add_slide(nar_pan, mmap, None)
        assert new_slide
        assert len(sidecar._slides) == 1

        im = Image(
            "https://www.nps.gov/npgallery/GetAsset/36106ED0-1DD8-B71C-07ED73544EA246C7/proxy/hires"
        )
        # Add action viewpoint to the slide
        sidecar.add_action(1, media=im)

        story.delete_story()



if __name__ == "__main__":
    unittest.main()
