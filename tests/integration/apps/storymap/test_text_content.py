import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Text, TextStyles, Button
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestTextContent(unittest.TestCase):
    """Test adding text and seeing properties"""

    def test_add_button(self):
        """Test adding a Button and seeing the properties"""
        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)
        btn = Button(
            link="https://www.nps.gov/subjects/forests/leaf-peeping.htm",
            text="Autumn Colors",
        )
        button = story.add(btn)

        assert button
        assert btn.properties

        item = gis.content.get(story._itemid)
        assert story.delete_story()

    def test_add_text(self):
        """Test adding Text of different styles and seeing properties"""
        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)
        welcome = Text(
            text="Welcome to a New Story About Some National Park Information",
            style=TextStyles.HEADING,
        )
        heading = story.add(welcome, position=2)
        park_quote = Text(
            text="I encourage everybody to hop on Google and type in 'national park' in whatever state they live in and see the beauty that lies in their own backyard. It's that simple.",
            style=TextStyles.QUOTE,
        )
        quote = story.add(park_quote, position=4)

        assert heading
        assert quote
        assert welcome.properties
        assert park_quote.properties

        paragraph = Text(
            text="This is a paragraph of text that is not styled.",
            style=TextStyles.PARAGRAPH,
            size="large",
        )
        assert story.add(paragraph)

        item = gis.content.get(story._itemid)
        assert story.delete_story()

    def test_get(self):
        """Test the get method for getting nodes by type and from an id"""
        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)
        welcome = Text(
            text="Welcome to a New Story About Some National Park Information",
            style=TextStyles.HEADING,
        )
        story.add(welcome, position=2)

        park_quote = Text(
            text="I encourage everybody to hop on Google and type in 'national park' in whatever state they live in and see the beauty that lies in their own backyard. It's that simple.",
            style=TextStyles.QUOTE,
        )
        story.add(park_quote, position=4)

        assert story.get(type="text")
        text = story.get(type="text")[0]
        text_id = list(text.keys())[0]
        assert story.get(node=text_id)

        item = gis.content.get(story._itemid)
        assert story.delete_story()


if __name__ == "__main__":
    unittest.main()
