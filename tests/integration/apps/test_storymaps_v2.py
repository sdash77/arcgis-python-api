import sys
from unittest.case import SkipTest

sys.path.insert(0, r"C:\\ipython_workfolder\\geosaurus\\src")
import unittest
from arcgis.gis import GIS
from arcgis.apps.storymap import StoryMap, Themes
from arcgis.apps.storymap import (
    Image,
    Audio,
    Map,
    Video,
    Embed,
    Button,
    Text,
    TextStyles,
    Gallery,
    Sidecar,
)

gis = GIS(profile="your_online_profile", verify_cert=False)

# Folder path for content (insert your own path)
content = r"C:\ipython_workfolder\Content"
# Create new storymap to use
story = StoryMap()


class TestStoryMap(unittest.TestCase):
    """Test Story Map"""

    assert story.nodes
    assert story.properties

    def test_storycover(self):
        """Change the storycover for the story"""
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

    def test_themes(self):
        """Change the story theme"""
        story.theme(Themes.SLATE)
        assert story.properties

    def test_add_image(self):
        """Test adding an Image and seeing properties"""
        img = Image(
            "https://www.nps.gov/npgallery/GetAsset/69680c29-caa3-42da-93d9-32925e9ed409/proxy/hires"
        )
        image = story.add(img, "Trees with a deer", "Sequoia trees in the distance")
        story.add()  # separator

        assert image
        assert img.properties
        assert img.caption
        assert img.alt_text

    def test_add_video(self):
        """Test adding a Video and seeing properties"""
        vid = Video(content + r"\underwater.mp4")
        video = story.add(vid)

        assert video
        assert vid.video

    def test_add_audio(self):
        """Test adding an Audio and seeing properties"""
        # Node order before adding audio
        aud = Audio(content + r"\craine.mp3")
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

    def test_add_embed(self):
        """Test adding Embed and seeing properties"""
        emb = Embed(
            "https://www.nps.gov/media/multimedia-search.htm#sort=Date_Last_Modified+desc"
        )
        web_page = story.add(emb)

        assert web_page
        assert emb.link
        assert emb.properties

    def test_add_button(self):
        """Test adding a Button and seeing the properties"""
        btn = Button(
            link="https://www.nps.gov/subjects/forests/leaf-peeping.htm",
            text="Autumn Colors",
        )
        button = story.add(btn)

        assert button
        assert btn.properties

    def test_add_map(self):
        """
        Test adding a Map and seeing the properties
        Map id can be changed if not found.
        """
        map_content = Map("006c10be294f4f64a5c9e5202cfa64c3")
        map = story.add(
            map_content, caption="This has nothing to do with parks but I needed a map"
        )

        assert map
        assert map_content.properties
        assert map_content.map
        assert map_content.caption

    def test_add_text(self):
        """Test adding Text of different styles and seeing properties"""
        welcome = Text(
            text="Welcome to a New Story About Some National Park Information",
            style=TextStyles.HEADING,
        )
        heading = story.add(welcome, position=2)
        park_quote = Text(
            text="I encourage everybody to hop on Google and type in ‘national park’ in whatever state they live in and see the beauty that lies in their own backyard. It’s that simple.",
            style=TextStyles.QUOTE,
        )
        quote = story.add(park_quote, position=4)

        assert heading
        assert quote
        assert welcome.properties
        assert park_quote.properties

    def test_get(self):
        """Test the get method for getting nodes by type and from an id"""
        assert story.get(type="text")
        text = story.get(type="text")[0]
        text_id = list(text.keys())[0]
        assert story.get(node=text_id)

    def test_delete(self):
        """Test delete method on an Audio node. Each content has this delete method"""
        # Audio through URL
        aud_dlt = Audio(content + r"\craine.mp3")
        story.add(aud_dlt)
        assert aud_dlt.properties

        deleted = aud_dlt.delete()
        assert deleted

    def test_replace_media_item(self):
        """Test replacing the webpage link. This can be done through a property for each content"""
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

    def test_path_to_url(self):
        vid = Video(content + r"\underwater.mp4")
        video = story.add(vid)

        new_video = "https://www.youtube.com/embed/G6b7Kgvd0iA"
        print(vid.video)

        vid.caption = "This is now a url"
        vid.video = new_video
        print(vid.video)
        print(vid.caption)

        assert vid.properties
        assert vid._url

    def test_create_gallery(self):
        """Test creating a gallery and adding images to it"""
        gallery = Gallery()
        assert gallery

        story.add(gallery)
        assert gallery.properties

        # Create Images to add to gallery
        i1 = Image(
            "https://www.nps.gov/npgallery/GetAsset/003805FB-155D-451F-6760BEF19A9F5039/proxy/hires"
        )
        i2 = Image(
            "https://www.nps.gov/npgallery/GetAsset/002E571C-155D-451F-6729E4B9B3830C6A/proxy/hires"
        )
        i3 = Image(
            "https://www.nps.gov/npgallery/GetAsset/003BA5FF-155D-451F-678D49A2F0585330/proxy/hires"
        )
        i4 = Image(
            "https://www.nps.gov/npgallery/GetAsset/00450151-155D-451F-67AF679D111DAD36/proxy/hires"
        )

        gallery.add_images([i1, i2, i3, i4])
        print(gallery.images)
        assert gallery.images

    def test_save(self):
        """Test saving the story"""
        saved = story.save()
        assert saved
        assert story._item

    def test_copy_and_delete(self):
        """Test copying story"""
        story_copy = story.duplicate("Story Copy")
        assert story_copy

        copy = StoryMap(story_copy)
        assert copy
        assert copy.delete_story()

    @SkipTest
    def test_delete(self):
        """Test deleting the main story"""
        assert story.delete_story()


if __name__ == "__main__":
    unittest.main()
