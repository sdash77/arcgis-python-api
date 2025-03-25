import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Code
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestEmbedContent(unittest.TestCase):
    """Test adding embed and seeing properties"""

    def test_add_embed(self):
        """Test adding Embed and seeing properties"""
        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)
        code = Code("from arcgis.gis imoprt GIS\ngis = GIS()", "py")
        code_block = story.add(code)

        assert code_block
        assert code_block.content
        assert code_block.language
        assert story.delete_story()

    def test_delete(self):
        """Test delete method on an Audio node. Each content has this delete method"""
        # Audio through URL
        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)

        code = Code("from arcgis.gis imoprt GIS\ngis = GIS()", "py")
        code_block = story.add(code)

        deleted = code_block.delete()
        assert deleted
        assert story.delete_story()

    def test_replace_code_item(self):
        """Test replacing the webpage link. This can be done through a property for each content"""
        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)
        code = Code("from arcgis.gis imoprt GIS\ngis = GIS()", "py")
        code_block = story.add(code)

        new_content = "Hello, this is plain text"
        new_lang = "txt"
        assert code_block.content
        print(code_block.content)

        code_block.content = new_content
        code_block.language = new_lang
        print(code_block.content)
        print(code_block.language)

        assert code_block.language
        assert story.delete_story()


if __name__ == "__main__":
    unittest.main()
