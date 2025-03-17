import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import (
    Briefing,
    Themes,
    Image,
    SlideLayout,
    SlideSubLayout,
    Text,
)
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestStoryMap(unittest.TestCase):
    """Test Basic Story Map Methods"""

    def test_creating_and_saving(self):
        """Change the storycover for the story"""
        # establish gis connection
        gis = self.gis
        briefing = Briefing(gis=gis)

        # assert some properties
        assert briefing.slides
        assert briefing

        # image for briefing cover
        river = Image(
            "https://www.nps.gov/npgallery/GetAsset/0022D3FF-1DD8-B71B-0BE3AD4C48F96FF9/proxy/hires"
        )

        # Edit briefing cover
        cover = briefing.slides[0].cover
        cover.title = "My First briefing"
        cover.summary = "Testing the Python API"
        cover.by_line = "Python Tester"
        cover.media = river

        """Change the story theme"""
        briefing.theme(Themes.SLATE)

        assert briefing.get_theme() == Themes.SLATE.value

        assert briefing.save()

        assert briefing.delete_briefing()

    def test_create_slide(self):
        # establish gis connection
        gis = self.gis
        briefing = Briefing(gis=gis)

        # assert some properties
        assert briefing.slides
        assert len(briefing.slides) == 1

        # Create a slide
        slide = briefing.add("single")

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
        assert isinstance(block.content, list)
        assert isinstance(block.content[0], Image)

        assert briefing.delete_briefing()

    def test_text_attachments(self):
        # establish gis connection
        gis = self.gis
        briefing = Briefing(gis=gis)
        briefing.delete_briefing()

    def test_slide_layouts(self):
        # establish gis connection
        gis = self.gis
        briefing = Briefing(gis=gis)

        # assert some properties
        assert briefing.slides
        assert len(briefing.slides) == 1

        # single layout
        single_slide = briefing.add(SlideLayout.SINGLE)
        assert single_slide.layout == SlideLayout.SINGLE.value
        assert len(single_slide.blocks) == 1

        # single slide without title
        single_no_title_slide = briefing.add(SlideLayout.TITLELESSSINGLE)
        single_no_title_slide.blocks[0].add_content(Text(content="Hello World"))
        assert single_no_title_slide.layout == SlideLayout.TITLELESSSINGLE.value
        assert len(single_no_title_slide.blocks) == 1

        # double slide
        double_slide = briefing.add(layout=SlideLayout.DOUBLE, sublayout=SlideSubLayout.THREE_SEVEN)
        double_slide.blocks[0].add_content(Text(content="Hello World"))
        assert double_slide.layout == SlideLayout.DOUBLE.value
        assert double_slide.sublayout == SlideSubLayout.THREE_SEVEN.value
        assert len(double_slide.blocks) == 2

        # double slide without title
        double_no_title_slide = briefing.add(
            SlideLayout.TITLELESSDOUBLE, sublayout=SlideSubLayout.SEVEN_THREE
        )
        double_no_title_slide.blocks[0].add_content(Text(content="Hello World"))
        assert double_no_title_slide.layout == SlideLayout.TITLELESSDOUBLE.value
        assert double_no_title_slide.sublayout == SlideSubLayout.SEVEN_THREE.value
        assert len(double_no_title_slide.blocks) == 2

        # change the sublayout
        double_no_title_slide.sublayout = SlideSubLayout.THREE_SEVEN
        assert double_no_title_slide.sublayout == SlideSubLayout.THREE_SEVEN.value

        # media only
        media_only_slide = briefing.add(SlideLayout.FULL)
        assert media_only_slide.layout == SlideLayout.FULL.value
        assert len(media_only_slide.blocks) == 1

        # section single
        section_single = briefing.add(SlideLayout.SECTIONSINGLE)
        assert section_single.layout == SlideLayout.SECTIONSINGLE.value

        # section double
        section_double = briefing.add(SlideLayout.SECTIONDOUBLE, section_position="end")
        assert section_double.layout == SlideLayout.SECTIONDOUBLE.value
        assert section_double.section_position == "end"
        assert len(section_double.blocks) == 1

        assert briefing.delete_briefing()


if __name__ == "__main__":
    unittest.main()
