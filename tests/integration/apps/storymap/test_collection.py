import sys
sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import Collection, Themes
from arcgis.apps.storymap import Image, Slide
from utils.decorators import integration_test

profiles = ["your_online_profile"]

@integration_test
class TestStoryMap(unittest.TestCase):
    """Test Basic Collection Methods"""

    def test_creating_and_saving(self):
        """Change the storycover for the story"""
        for profile in profiles:
            with self.subTest(msg=profile):
                # establish gis connection
                gis = GIS(profile=profile, verify_cert=False)
                collection = Collection()

                # assert some properties
                assert len(collection.content) == 0
                assert collection

                # Edit briefing cover
                collection.cover(
                    "My First Collection",
                    summary="Testing the Python API",
                    by_line="Python Tester",
                )

                """Change the story theme"""
                collection.theme(Themes.SLATE)

                assert collection.save()

                assert collection.delete_collection()

    def test_add_item(self):
        for profile in profiles:
            with self.subTest(msg=profile):
                # establish gis connection
                gis = GIS(profile=profile, verify_cert=False)
                collection = Collection()

                # assert some properties
                assert len(collection.content) == 0
                assert collection

                item = gis.content.search("USA", item_type="Storymap", outside_org=True)[0]
                collection.add(item, title="USA")

                assert len(collection.content) == 1

                collection.remove(0)

                assert len(collection.content) == 0

                assert collection.delete_collection()


if __name__ == "__main__":
    unittest.main()
