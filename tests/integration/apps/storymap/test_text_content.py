import unittest
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Text, TextStyles, Button
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestTextContent(unittest.TestCase):
    """Test adding text and seeing properties"""

    def setUp(self):
        self.story = StoryMap(gis=self.gis)

    def tearDown(self):
        self.story.delete_story()

    def test_add_button(self):
        """Test adding a Button and seeing the properties"""
        # establish gis connection
        btn = Button(
            link="https://www.nps.gov/subjects/forests/leaf-peeping.htm",
            text="Autumn Colors",
        )
        button = self.story.add(btn)

        assert button
        print(btn.properties)
        assert btn.properties

    def test_add_text(self):
        """Test adding Text of different styles and seeing properties"""
        # establish gis connection
        welcome = Text(
            text="Welcome to a New Story About Some National Park Information",
            style=TextStyles.HEADING,
        )
        heading = self.story.add(welcome, position=2)
        park_quote = Text(
            text="I encourage everybody to hop on Google and type in 'national park' in whatever state they live in and see the beauty that lies in their own backyard. It's that simple.",
            style=TextStyles.QUOTE,
        )
        quote = self.story.add(park_quote, position=4)

        assert heading
        assert quote
        print(welcome.properties)
        assert welcome.properties
        assert park_quote.properties

        paragraph = Text(
            text="This is a paragraph of text that is not styled.",
            style=TextStyles.PARAGRAPH,
            size="large",
        )
        assert self.story.add(paragraph)

    def test_get_text(self):
        """Test getting text node through content_list"""
        # establish gis connection
        welcome = Text(
            text="Welcome to a New Story About Some National Park Information",
            style=TextStyles.HEADING,
        )
        self.story.add(welcome, position=2)

        park_quote = Text(
            text="I encourage everybody to hop on Google and type in 'national park' in whatever state they live in and see the beauty that lies in their own backyard. It's that simple.",
            style=TextStyles.QUOTE,
        )
        self.story.add(park_quote, position=4)

        text_welcome = self.story.content_list[2]
        assert isinstance(text_welcome, Text)
        assert text_welcome.properties['node_dict']['data']['type'] == TextStyles.HEADING.value
        text_park = self.story.content_list[3]
        assert isinstance(text_park, Text)
        assert text_park.properties['node_dict']['data']['type'] == TextStyles.QUOTE.value


if __name__ == "__main__":
    unittest.main()
