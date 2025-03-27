import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Audio
from utils.decorators import integration_test, profiles
from integration.config import QALAB_ROOT_PATH

### ***** Before running this test you need to download the audio file below and correct the path in the test *****
# audio: https://www.nps.gov/media/video/view.htm?id=E5833EE1-4BC7-47B8-832F-EBDE023E6E51


@integration_test
@profiles.enterprise_and_agol
class TestAudioContent(unittest.TestCase):
    """Test adding audio and seeing properties"""

    def test_add_audio(self):
        """Test adding Embed and seeing properties"""
        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)

        import os

        file = os.path.join(QALAB_ROOT_PATH, "storymaps_tests", "content", "rocks.mp3")
        # file = r"C:\ipython_workfolder\Content\rocks.mp3"
        if os.path.isfile(file):
            aud = Audio(file)
            print("Node Order Before Adding Audio:")
            print(story.content_list)
            print("------------------------------------")
            # Add audio at a certain position
            audio = story.add(aud, position=2)
            separator = story.add()

            # See node order after audio was added
            print("Node Order After Adding Audio:")
            print(story.content_list)

            assert audio
            assert separator
            assert isinstance(story.content_list, list) and len(story.content_list) > 0

        assert story.delete_story()


if __name__ == "__main__":
    unittest.main()
