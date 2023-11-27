# import sys
# sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.gis import GIS, Item
from arcgis.apps.storymap import Collection, Themes
from arcgis.apps.storymap import Image, Slide

profiles = ["your_online_profile", "your_enterprise_profile"]


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
                assert collection.content
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

    def test_create_slide(self):
        for profile in profiles:
            with self.subTest(msg=profile):
                # establish gis connection
                gis = GIS(profile=profile, verify_cert=False)
                briefing = Briefing()

                # assert some properties
                assert briefing.slides
                assert len(briefing.slides) == 1

                # Create a slide
                slide = Slide(layout="single")
                briefing.add(slide)

                # assert some properties
                assert briefing.slides
                assert len(briefing.slides) == 2
                assert slide.blocks
                assert len(slide.blocks) == 1

                # add an image to the block
                block = slide.blocks[0]
                img = Image(
                    "https://www.nps.gov/npgallery/GetAsset/0022D3FF-1DD8-B71B-0BE3AD4C48F96FF9/proxy/hires"
                )
                block.add_content(img)
                assert block.content
                assert isinstance(block.content, Image)

                assert briefing.delete_briefing()


if __name__ == "__main__":
    unittest.main()
