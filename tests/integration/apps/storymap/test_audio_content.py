# import sys
# sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Audio
from utils.decorators import integration_test

### ***** Before running this test you need to download the audio file below and correct the path in the test *****
# audio: https://www.nps.gov/media/video/view.htm?id=E5833EE1-4BC7-47B8-832F-EBDE023E6E51

profiles = ["your_online_profile", "your_enterprise_profile"]

@integration_test
class TestAudioContent(unittest.TestCase):
    """Test adding audio and seeing properties"""

    def test_add_audio(self):
        """Test adding Embed and seeing properties"""
        for profile in profiles:
            with self.subTest(msg=profile):
                # establish gis connection
                gis = GIS(profile=profile, verify_cert=False)
                story = StoryMap()

                import os

                file = r"C:\ipython_workfolder\Content\rocks.mp3"
                if os.path.isfile(file):
                    aud = Audio(file)
                    print("Node Order Before Adding Audio:")
                    print(story.nodes)
                    print("------------------------------------")
                    # Add audio at a certain position
                    audio = story.add(aud, position=2)
                    separator = story.add()

                    # See node order after audio was added
                    print("Node Order After Adding Audio:")
                    print(story.nodes)

                    assert audio
                    assert separator
                    assert story.nodes

                item = gis.content.get(story._itemid)
                assert item.delete()


if __name__ == "__main__":
    unittest.main()
