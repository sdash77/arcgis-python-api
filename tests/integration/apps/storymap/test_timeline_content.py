# import sys
# sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Image, Timeline, Text
from utils.decorators import integration_test


@integration_test
class TestSideCar(unittest.TestCase):
    """Test Story Map Timeline content"""

    def test_create_timeline(self):
        gis = GIS(profile="your_online_profile")

        timeline = Timeline("single-side")

        assert timeline

        story = StoryMap(gis=gis)
        story.add(timeline)

        assert len(story.content_list) == 4
        assert isinstance(story.content_list[2], Timeline)

        story.delete_story()

    def add_content_to_timeline(self):
        print("Testing adding")
        gis = GIS(profile="your_online_profile")

        timeline = Timeline("single-side")

        assert timeline

        story = StoryMap(gis=gis)
        story.add(timeline)

        assert len(story.content_list) == 4
        assert isinstance(story.content_list[2], Timeline)

        # Construct items that will go into new slide
        im = Image(
            "https://www.nps.gov/npgallery/GetAsset/36106ED0-1DD8-B71C-07ED73544EA246C7/proxy/hires"
        )
        txt = Text("This is a grizzly bear.")
        txt2 = Text("They can be found in some of our national parks.")

        timeline.add_event([im, txt])
        timeline.add_event([txt2])
        assert timeline.properties

        story.delete_story()


if __name__ == "__main__":
    unittest.main()
