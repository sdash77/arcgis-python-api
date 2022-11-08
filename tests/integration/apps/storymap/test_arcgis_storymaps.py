# import sys
# sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.gis import GIS, Item
from arcgis.apps.storymap import StoryMap, Themes
from arcgis.apps.storymap import (
    Image,
)

profiles = ["your_online_profile", "your_enterprise_profile"]

class TestStoryMap(unittest.TestCase):
    """Test Basic Story Map Methods"""


    def test_creating_and_saving(self):
        """Change the storycover for the story"""
        for profile in profiles:
             with self.subTest(msg=profile):
                # establish gis connection
                gis = GIS(profile=profile, verify_cert=False)
                story = StoryMap()
                assert story.nodes
                assert story.properties
                # image for story cover
                river = Image(
                    "https://www.nps.gov/npgallery/GetAsset/0022D3FF-1DD8-B71B-0BE3AD4C48F96FF9/proxy/hires"
                )

                # Edit story cover
                story.cover(
                    "My First Story",
                    type="minimal",
                    summary="Testing the Python API",
                    by_line="Python Tester",
                    image=river,
                )
                assert story.cover_date
                assert story.nodes

                """Change the story theme"""
                story.theme(Themes.SLATE)
                assert story.properties

                assert story.save()

                item = gis.content.get(story._itemid)
                assert item.delete()

if __name__ == "__main__":
    unittest.main()
