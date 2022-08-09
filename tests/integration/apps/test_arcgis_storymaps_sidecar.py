import sys
from unittest.case import SkipTest


sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.gis import GIS, Item
import json
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Embed, Image, Sidecar, Text

gis = GIS(profile="your_online_profile", verify_cert=False)

# Get storymap that already has a sidecar in it
story = StoryMap("a35f4fd9aeac46a0bed6a1ea38d4f003")


class TestStoryMapSideCar(unittest.TestCase):
    """Test Story Map Sidecar methods"""

    assert story.nodes

    # Find the node id for the sidecar
    for node in story.nodes:
        for key in node:
            if node[key] is "Sidecar":
                sc_node = key
                break

    # Get the sidecar
    sidecar = story.get(sc_node)
    assert isinstance(sidecar, Sidecar)
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
    assert len(sidecar._slides) == 2

    # remove the slide
    sidecar.remove_slide(new_slide["New Slide"])
    assert len(sidecar._slides) == 1


if __name__ == "__main__":
    unittest.main()
