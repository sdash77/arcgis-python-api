import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Embed
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
        emb = Embed(
            "https://www.nps.gov/media/multimedia-search.htm#sort=Date_Last_Modified+desc"
        )
        web_page = story.add(emb)

        assert web_page
        assert emb.link
        assert emb.properties
        item = gis.content.get(story._itemid)
        assert story.delete_story()

    def test_delete(self):
        """Test delete method on an Audio node. Each content has this delete method"""
        # Audio through URL
        # establish gis connection
        gis = self.gis
        story = StoryMap(gis=gis)

        emb = Embed(
            "https://www.nps.gov/media/multimedia-search.htm#sort=Date_Last_Modified+desc"
        )
        story.add(emb)

        deleted = emb.delete()
        assert deleted
        item = gis.content.get(story._itemid)
        assert story.delete_story()


def test_replace_media_item(self):
    """Test replacing the webpage link. This can be done through a property for each content"""
    # establish gis connection
    gis = self.gis
    story = StoryMap(gis=gis)
    emd = Embed(
        "https://www.nps.gov/media/multimedia-search.htm#sort=Date_Last_Modified+desc"
    )
    story.add(emd)

    new_emd = "https://www.nps.gov/index.htm"
    assert emd.link
    print(emd.link)

    emd.link = new_emd
    emd.caption = "I updated the webpage"
    print(emd.link)
    print(emd.caption)

    assert emd.link
    item = gis.content.get(story._itemid)
    assert story.delete_story()


if __name__ == "__main__":
    unittest.main()
