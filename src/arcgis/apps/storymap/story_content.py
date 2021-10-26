import os
import PIL.Image
import mimetypes
from typing import Optional, Union
import uuid
from urllib.parse import urlparse
from arcgis import env
from arcgis.gis import Item


class Image(object):
    """
    Class representing an image from a url or file
    """

    def __init__(
        self,
        path: str = None,
    ):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        path                    Required String. The file path to the image that will be added.
        ==================      ====================================================================
        """
        self._path = path

        # assign ids
        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._resource_node = "r-" + uuid.uuid4().hex[0:6]
        mt = mimetypes.guess_type(path)[0].lower()
        self._ext_type = mt.split("/")[1]

    # ----------------------------------------------------------------------
    def _add_image(self, story, caption=None, alt_text=None, display=None):
        # Make an add resource call
        story._add_resource(self._path)

        # Create image nodes
        story.properties["nodes"][self._node] = {
            "type": "image",
            "data": {
                "image": self._resource_node,
                "caption": caption,
                "alt": alt_text,
            },
            "config": {"size": display},
        }

        im = PIL.Image.open(self._path)
        w, h = im.size
        # Create resource node
        story.properties["resources"][self._resource_node] = {
            "type": "image",
            "data": {
                "resourceId": os.path.basename(os.path.normpath(self._path)),
                "provider": "item-resource",
                "height": h,
                "width": w,
            },
        }

    # ----------------------------------------------------------------------
    def _update_image(self, node_id, story):
        resource_node_id = story.properties["nodes"][node_id]["data"]["image"]
        # Update the height and width for the image
        im = PIL.Image.open(self._path)
        w, h = im.size
        story.properties["resources"][resource_node_id]["data"]["height"] = h
        story.properties["resources"][resource_node_id]["data"]["width"] = w

        # UPDATE RESOURCE
        resource_id = story.properties["resources"][resource_node_id]["data"][
            "resourceId"
        ]
        story.properties["resources"][resource_node_id]["data"][
            "resourceId"
        ] = os.path.basename(os.path.normpath(self._path))
        # Update ids
        self._node = node_id
        self._resource_node = resource_node_id
        # Update the resource
        story._remove_resource(resource_id)
        story._add_resource(self._path)


###############################################################################################################
class Video(object):
    """
    Class representing a video from a url or file
    """

    def __init__(
        self,
        path: str = None,
    ):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        path                    Required String. The file path to the video that will be added.
        ==================      ====================================================================
        """
        self._path = path

        # assign ids
        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._resource_node = "r-" + uuid.uuid4().hex[0:6]

        mt = mimetypes.guess_type(path)[0].lower()
        self._ext_type = mt.split("/")[1]

    # ----------------------------------------------------------------------
    def _add_video(self, story, caption=None, alt_text=None, display=None):
        # Make an add resource call
        story._add_resource(self._path)

        # Create image nodes
        story.properties["nodes"][self._node] = {
            "type": "video",
            "data": {
                "video": self._resource_node,
                "caption": caption,
                "alt": alt_text,
            },
            "config": {
                "size": display,
            },
        }

        # Create resource node
        story.properties["resources"][self._resource_node] = {
            "type": "video",
            "data": {
                "resourceId": os.path.basename(os.path.normpath(self._path)),
                "provider": "item-resource",
            },
        }

    # ----------------------------------------------------------------------
    def _update_video(self, node_id, story):
        resource_node_id = story.properties["nodes"][node_id]["data"]["video"]
        # UPDATE RESOURCE
        resource_id = story.properties["resources"][resource_node_id]["data"][
            "resourceId"
        ]
        story.properties["resources"][resource_node_id]["data"][
            "resourceId"
        ] = os.path.basename(os.path.normpath(self._path))
        # Update ids
        self._node = node_id
        self._resource_node = resource_node_id
        # Update the resource
        story._remove_resource(resource_id)
        story._add_resource(self._path)


###############################################################################################################
class Audio(object):
    """
    Class representing an audio from a url or file

    """

    def __init__(
        self,
        path: str = None,
    ):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        path                    Required String. The file path to the image that will be added.
        ==================      ====================================================================
        """

        self._path = path

        # assign ids
        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._resource_node = "r-" + uuid.uuid4().hex[0:6]

    # ----------------------------------------------------------------------
    def _add_audio(self, story, caption=None, alt_text=None, display=None):
        # Make an add resource call
        story._add_resource(self._path)

        # Create image nodes
        story.properties["nodes"][self._node] = {
            "type": "audio",
            "data": {
                "video": self._resource_node,
                "caption": caption,
                "alt": alt_text,
            },
            "config": {"size": display},
        }

        # Create resource node
        story.properties["resources"][self._resource_node] = {
            "type": "audio",
            "data": {
                "resourceId": os.path.basename(os.path.normpath(self._path)),
                "provider": "item-resource",
            },
        }

    # ----------------------------------------------------------------------
    def _update_audio(self, node_id, story):
        resource_node_id = story.properties["nodes"][node_id]["data"]["video"]
        # UPDATE RESOURCE
        resource_id = story.properties["resources"][resource_node_id]["data"][
            "resourceId"
        ]
        story.properties["resources"][resource_node_id]["data"][
            "resourceId"
        ] = os.path.basename(os.path.normpath(self._path))
        # Update ids
        self._node = node_id
        self._resource_node = resource_node_id
        # Update the resource
        story._remove_resource(resource_id)
        story._add_resource(self._path)


###############################################################################################################
class WebPage(object):
    """
    Class representing a hyperlink from a url
    """

    def __init__(
        self,
        path: str = None,
    ):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        path                    Required String. The file path to the audio that will be added.
        ==================      ====================================================================
        """
        self._path = path
        self._node = "n-" + uuid.uuid4().hex[0:6]

    # ----------------------------------------------------------------------
    def _add_webpage(self, story, caption=None, alt_text=None):

        sections = urlparse(self._path)

        # Create embed nodes
        story.properties["nodes"][self._node] = {
            "type": "embed",
            "data": {
                "url": self._path,
                "embedType": "link",
                "title": sections.netloc,
                "description": caption,
                "providerUrl": self._path,
                "alt": alt_text,
                "display": "card",
            },
        }

    # ----------------------------------------------------------------------
    def _update_webpage(self, node_id, story):
        # Update ids
        self._node = node_id
        sections = urlparse(self._path)

        story.properties["nodes"][node_id]["data"]["url"] = self._path
        story.properties["nodes"][node_id]["data"]["title"] = sections.netloc
        story.properties["nodes"][node_id]["data"]["providerUrl"] = self._path


###############################################################################################################
class Text(object):
    """
    Class representing a text

    """

    def __init__(self, text: str = None, style: str = "paragraph", color: str = "000"):
        """

        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        text                    Required String. The text that will be shown in the story.

                                Example:
                                    "Paragraph with <strong>bold</strong>,
                                    <em>italic</em> and
                                    <a href=\"https://www.google.com\" rel=\"noopener noreferrer\"
                                    target=\"_blank\">hyperlink</a> and a
                                    <span class=\"sm-text-color-080\">custom color</span>"
        ------------------      --------------------------------------------------------------------
        style                   Optional String. There are 6 different styles of text that can be
                                added to a story.

                                Values: 'paragraph' | 'heading' | 'subheading' | 'numbered-list' |
                                        'bullet-list' | 'quote' | 'large-paragraph'

                                ..note:
                                    To make text withing these types bold, italic, or hyperlink the
                                    text parameter must include these.
        ------------------      --------------------------------------------------------------------
        custom_color            Optional String. The hex color value without the #.
                                Only available when type is either 'paragraph', 'bullet-list', or
                                'numbered-list'.

                                Ex: custom_color = "080"
        ==================      ====================================================================


        Properties of the different text types:

        ===================     ====================================================================
        **Type**                **Text**
        -------------------     --------------------------------------------------------------------
        paragraph               String can contain the following tags for text formatting:
                                <strong>, <em>, <a href="{link}" rel="noopener noreferer” target=”_blank”
                                and a class attribute to indicate color formatting:
                                class=sm-text-color-{values} attribute in the <strong> | <em> | <a> | <span> tags

                                Values: themeColor1 | themeColor2 | themeColor3 | customTextColors
        -------------------     --------------------------------------------------------------------
        large-paragraph         String can contain the following tags for text formatting:
                                <strong>, <em>, <a href="{link}" rel="noopener noreferer” target=”_blank”
                                and a class attribute to indicate color formatting:
                                class=sm-text-color-{values} attribute in the <strong> | <em> | <a> | <span> tags

                                Values: themeColor1 | themeColor2 | themeColor3 | customTextColors
        -------------------     --------------------------------------------------------------------
        heading                 String can only contain <em> tag
        -------------------     --------------------------------------------------------------------
        subheading              String can only contain <em> tag
        -------------------     --------------------------------------------------------------------
        bullet-list             String can contain the following tags for text formatting:
                                <strong>, <em>, <a href="{link}" rel="noopener noreferer” target=”_blank”
                                and a class attribute to indicate color formatting:
                                class=sm-text-color-{values} attribute in the <strong> | <em> | <a> | <span> tags

                                Values: themeColor1 | themeColor2 | themeColor3 | customTextColors
        -------------------     --------------------------------------------------------------------
        numbered-list           String can contain the following tags for text formatting:
                                <strong>, <em>, <a href="{link}" rel="noopener noreferer” target=”_blank”
                                and a class attribute to indicate color formatting:
                                class=sm-text-color-{values} attribute in the <strong> | <em> | <a> | <span> tags

                                Values: themeColor1 | themeColor2 | themeColor3 | customTextColors
        -------------------     --------------------------------------------------------------------
        quote                   String can only contain <strong> and <em> tags
        ===================     ====================================================================

        """
        self._node = uuid.uuid4().hex[0:6]
        self._text = text

        # Handle style types
        style = style.lower().strip(" ")
        if style == "heading":
            style = "h2"
        if style == "subheading":
            style = "h3"
        if "bullet" in style:
            style = "bullet-list"
        if "number" in style:
            style = "numbered-list"
        if "large" in style:
            style = "large-paragraph"
        self._style = style

        # Color only applies certain styles
        if style in ["paragraph", "large-paragraph", "bullet-list", "numbered-list"]:
            self._color = color
        else:
            self._color = None

    # ----------------------------------------------------------------------
    def _add_text(self, story):

        story.properties["nodes"][self._node] = {
            "type": "text",
            "data": {
                "type": self._style,
                "text": self._text,
            },
        }
        if self._color is not None:
            story.properties["nodes"][self._node]["data"]["customTextColors"] = [
                self._color
            ]

    # ----------------------------------------------------------------------
    def _update_text(self, node_id, story):
        if self._text is not None:
            story.properties["nodes"][node_id]["data"]["text"] = self._text
        if self._style is not None:
            story.properties["nodes"][node_id]["data"]["type"] = self._style
        self._node = node_id


###############################################################################################################
class Button(object):
    """
    Class representing a button
    """

    def __init__(self, link: str = None, text: str = None):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        link                    Required String. When user clicks on button, they will be brought to
                                the link.
        ------------------      --------------------------------------------------------------------
        text                    Required String. The text that shows on the button.
        ==================      ====================================================================

        """
        self._node = uuid.uuid4().hex[0:6]
        self._link = link
        self._text = text

    # ----------------------------------------------------------------------
    def _add_button(self, story):
        story.properties["nodes"][self._node] = {
            "type": "button",
            "data": {"text": self._text, "link": self._link},
        }

    # ----------------------------------------------------------------------
    def _update_button(self, node_id, story):
        if self._text is not None:
            story.properties["nodes"][node_id]["data"]["text"] = self._text
        if self._link is not None:
            story.properties["nodes"][node_id]["data"]["link"] = self._link
        self._node = node_id


###############################################################################################################
class Map(object):
    """
    Class representing a webmap or webscene for the story

    """

    def __init__(
        self,
        item: Item,
    ):
        """
        =================       ====================================================================
        **Argument**            **Description**
        -----------------       --------------------------------------------------------------------
        item                    An Item of type WebMap or WebScene or a String representing the item
                                id to add to the story map.
        =================       ====================================================================

        """

        # If string id get the item
        if isinstance(item, str):
            item = env.active_gis.content.get(item)

        # Create map object to extract properties
        if isinstance(item, Item):
            map_item = env.active_gis.map(item)

        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._resource_node = "r-" + item.id

        # Assign properties
        self._path = item
        self._show_legend = map_item.legend
        self._center = map_item.center
        self._zoom = map_item.zoom
        self._extent = map_item.extent
        self._map_layers = map_item.layers
        self._type = item.type

    # ----------------------------------------------------------------------
    def _add_webmap(self, story, caption=None, alt_text=None, display=None):
        # Create webmap nodes
        story.properties["nodes"][self._node] = {
            "type": "webmap",
            "data": {
                "map": self._resource_node,
                "caption": caption,
                "alt": alt_text,
                "mapLayers": self._map_layers,
                "extent": self._extent,
                "center": self._center,
                "zoom": self._zoom,
                "showLegend": self._show_legend,
            },
            "config": {"size": display},
        }

        # Create resource node
        story.properties["resources"][self._resource_node] = {
            "type": "webmap",
            "data": {
                "extent": self._extent,
                "center": self._center,
                "zoom": self._zoom,
                "mapLayers": self._map_layers,
                "itemId": self._path.id,
                "itemType": self._type,
                "type": "default",
                "showLegend": self._show_legend,
            },
        }

    # ----------------------------------------------------------------------
    def _update_map(self, node_id, story):
        # Update all properties that change with new map
        node_dict = story.properties["nodes"][node_id]["data"]
        resouce_node = node_dict["map"]
        resource_dict = story.properties["resources"][resouce_node]["data"]
        # Update node_dict
        node_dict["mapLayer"] = self._map_layers
        node_dict["extent"] = self._extent
        node_dict["center"] = self._center
        node_dict["zoom"] = self._zoom
        node_dict["showLegend"] = self._show_legend

        # Update resource_dict
        resource_dict["mapLayer"] = self._map_layers
        resource_dict["extent"] = self._extent
        resource_dict["center"] = self._center
        resource_dict["zoom"] = self._zoom
        resource_dict["showLegend"] = self._show_legend
        resouce_node["itemId"] = self._path.id
        resouce_node["itemType"] = self._type

        # Update ids
        self._node = node_id
        self._resource_node = resouce_node


###############################################################################################################
class Swipe(object):
    def __init__(self, node_id: str, story):
        """
        Create an Swipe immersive object from a pre-existing immersive node.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        node_id             Required String. The node id for the swipe type.
        ---------------     --------------------------------------------------------------------
        story               Required StoryMap that the swipe belongs to.
        ===============     ====================================================================
        """
        node = story.properties["nodes"][node_id]
        self._node_id = node_id
        self._type = node["type"]
        self._data = node["data"]
        self._content = node["data"]["contents"]

    # ----------------------------------------------------------------------
    def edit(
        self,
        story,
        item: Optional[Union[Image, Map]] = None,
        caption: Optional[str] = None,
        alt_text: Optional[str] = None,
        position: str = "right",
        display: Optional[str] = None,
    ):
        """
        Add and item to the story map

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        story               Required StoryMap that the swipe belongs to.
        ---------------     --------------------------------------------------------------------
        item                Optional item of type: Image or Map.
        ---------------     --------------------------------------------------------------------
        caption             Optional String. If item is specified, the caption will be used for
                            the item. If item is None then caption is used for the swipe node.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional String. If item is specified, the alt_text will be used for
                            the item. If item is None then alt_text is used for the swipe node.
        ---------------     --------------------------------------------------------------------
        position            Optional String. There are two positions for a swipe node: 'right'
                            or 'left'. If item parameter is not none then position is default
                            to 'right'. If no item is given, this parameter is ignored.
        ---------------     --------------------------------------------------------------------
        display             Optional String. Display for the swipe node.

                            Values: "small" | "medium" | "large"
        ===============     ====================================================================

        """
        node = story.properties["nodes"][self._node_id]
        if item is not None:
            if not isinstance(item, Image) or not isinstance(item, Map):
                raise Exception("Swipe nodes can only accept Image or Map item type")
            # If user has created the item but not added to the story yet.
            if item._node not in story.properties["nodes"]:
                if isinstance(item, Image):
                    item._add_image(story, caption, alt_text)
            elif isinstance(item, Map):
                item._add_webmap(story, caption, alt_text)
            # Add to content in position wanted
            if position == "left":
                node["data"]["content"]["0"] = item._node
            else:
                node["data"]["content"]["1"] = item._node
        else:
            if caption is not None:
                node["data"]["caption"] = caption
            if alt_text is not None:
                node["data"]["alt"] = alt_text
            if display is not None:
                node["config"]["size"] = display


###############################################################################################################
class Sidecar(object):
    def __init__(self, node_id: str, story):
        """
        Create an Sidecar immersive object from a pre-existing immersive node.

        A sidecar is composed of slides. Slides are composed of two nodes: a narrative panel and a media node.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        node_id             Required String. The node id for the sidecar type.
        ---------------     --------------------------------------------------------------------
        story               Required StoryMap that the sidecar belongs to.
        ===============     ====================================================================
        """
        self._story = story
        node = story.properties["nodes"][node_id]
        self._node_id = node_id
        self._type = node["data"]["type"]
        if self._type != "sidecar":
            raise Exception("This node is not of type sidecar.")
        self._subtype = node["data"]["subtype"]
        self._slides = node["children"]

    # ----------------------------------------------------------------------
    def edit_slide(
        self,
        item: Union[Image, Video, Map, Text, WebPage],
        slide_number: int,
    ):
        """
        Edit slide text or media item. Item can be of type Image, Video, Map, or WebPage.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        item                Required item to replace current media item.
                            Item type can be Image, Video, Map, WebPage or Text.
        ---------------     --------------------------------------------------------------------
        slide_number        Required Integer. The slide that will be edited. First slide is 1.
        ===============     ====================================================================
        """
        # Find children nodes
        slide = self._slides[slide_number - 1]
        slide_node = self._story.properties["nodes"][slide]
        narrative_panel = slide_node["children"][0]
        media_item = None
        if len(slide_node["children"]) == 2:
            media_item = slide_node["children"][1]

        # Check to see if item has been added to node properties
        if item._node not in self._story.properties["nodes"]:
            self._add_item_story(item)

        # Insert new item
        if isinstance(item, Text):
            # If item is text then update the narrative panel by removing old text and adding new
            old_text_node = narrative_panel["children"][0]
            narrative_panel["children"].pop(0)
            self._story.delete(old_text_node)
            narrative_panel["children"].insert(0, item._node)
        else:
            # Remove current media item and add new item as media
            if media_item:
                self._story.delete(media_item)
                slide_node["children"].pop(1)
            slide_node["children"].insert(1, item._node)

    # ----------------------------------------------------------------------
    def remove_slide(self, slide_number: int):
        """
        Remove a slide from the sidecar.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        slide_number        Required Integer. The slide that will be removed. First slide is 1.
        ===============     ====================================================================
        """
        # Remove slide and all associated children.
        slide = self._slides[slide_number - 1]
        self._slide.remove(slide_number - 1)
        self._story.delete(slide)
        self._remove_associated(slide)

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        List all slides and their children

        :return:
            A list where the first item is the node id for the sidecar. Next
            items are dictionary of slides and their children.
        """
        sidecar_tree = [self._node_id]
        for slide in self._slides:
            narrative_panel = self._story.properties["nodes"][slide]["children"][0]
            text = self._story.properties["nodes"][narrative_panel]["children"]
            media_item = self._story.properties["nodes"][slide]["children"][1]
            sidecar_tree.append(
                {
                    "Slide: "
                    + slide: [
                        "Narrative Panel: " + narrative_panel,
                        "Text: " + text[0],
                        "Media Item: " + media_item,
                    ]
                }
            )
        return sidecar_tree

    # ----------------------------------------------------------------------
    def _remove_associated(self, slide):
        # Remove narrative panel and text associated
        narrative_panel = self._story.properties["nodes"][slide]["children"][0]
        self._story.delete(narrative_panel["children"][0])
        self._story.delete(narrative_panel)
        # Remove media item
        media_item = self._story.properties["nodes"][slide]["children"][1]
        self._story.delete(media_item)

    # ----------------------------------------------------------------------
    def _add_item_story(self, item):
        if isinstance(item, Image):
            item._add_image(self._story)
        elif isinstance(item, Video):
            item._add_video(self._story)
        elif isinstance(item, WebPage):
            item._add_webpage(self._story)
        elif isinstance(item, Map):
            item._add_webmap(self._story)
        elif isinstance(item, Text):
            item._add_text()


###############################################################################################################
class Slideshow(object):
    def __init__(self, node_id: str, story):
        """
        Create an Slideshow immersive object from a pre-existing immersive node.

        A slideshow is composed of slides. Slides are composed of two nodes: a narrative panel and a media node.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        node_id             Required String. The node id for the slideshow type.
        ---------------     --------------------------------------------------------------------
        story               Required StoryMap that the slideshow belongs to.
        ===============     ====================================================================
        """
        self._story = story
        node = story.properties["nodes"][node_id]
        self._node_id = node_id
        self._type = node["data"]["type"]
        if self._type != "slideshow":
            raise Exception("This node is not of type slideshow")
        self._slides = node["children"]

    # ----------------------------------------------------------------------
    def edit_slide(self, item: Union[Image, Video, Map, Text], slide_number: int):
        """
        Edit slide text or media item. Media item can be an Image, Video, or Map.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        item                Required item to replace current media item.
                            Item type can be Image, Video, Map, or Text.
        ---------------     --------------------------------------------------------------------
        slide_number        Required Integer. The slide that will be edited. First slide is 1.
        ===============     ====================================================================
        """
        # Find children
        slide = self._slides[slide_number - 1]
        slide_node = self._story.properties["nodes"][slide]
        narrative_panel = slide_node["children"][0]
        media_item = slide_node["children"][1]

        # Check to see if item has been added to node properties
        if item._node not in self._story.properties["nodes"]:
            self._add_item_story(item)

        # Insert new item
        if isinstance(item, Text):
            # If item is text then update the narrative panel by removing old text and adding new
            old_text_node = narrative_panel["children"][0]
            narrative_panel["children"].pop(0)
            self._story.delete(old_text_node)
            narrative_panel["children"].insert(0, item._node)
        else:
            # Remove current media item and add new item as media
            if media_item:
                self._story.delete(media_item)
                slide_node["children"].pop(1)
            slide_node["children"].insert(1, item._node)

    # ----------------------------------------------------------------------
    def remove_slide(self, slide_number: int):
        """
        Remove a slide from a slideshow.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        slide_number        Required Integer. The slide that will be removed. First slide is 1.
        ===============     ====================================================================
        """
        # Remove slide and all associated children.
        slide = self._slides[slide_number - 1]
        self._slide.remove(slide_number - 1)
        self._story.delete(slide)
        self._remove_associated(slide)

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        List all slides and their children

        :return:
            A list where the first item is the node id for the slideshow. Next
            items are dictionary of slides and their children.
        """
        slideshow_tree = [self._node_id]
        for slide in self._slides:
            narrative_panel = self._story.properties["nodes"][slide]["children"][0]
            text = self._story.properties["nodes"][narrative_panel]["children"]
            media_item = self._story.properties["nodes"][slide]["children"][1]
            slideshow_tree.append(
                {
                    "Slide: %s"
                    % slide: [
                        "Narrative Panel: " + narrative_panel,
                        "Text: " + text[0],
                        "Media Item: " + media_item,
                    ]
                }
            )
        return slideshow_tree

    # ----------------------------------------------------------------------
    def _remove_associated(self, slide):
        # Remove narrative panel and text associated
        narrative_panel = self._story.properties["nodes"][slide]["children"][0]
        self._story.delete(narrative_panel["children"][0])
        self._story.delete(narrative_panel)
        # Remove media item
        media_item = self._story.properties["nodes"][slide]["children"][1]
        self._story.delete(media_item)

    # ----------------------------------------------------------------------
    def _add_item_story(self, item):
        if isinstance(item, Image):
            item._add_image(self._story)
        elif isinstance(item, Video):
            item._add_video(self._story)
        elif isinstance(item, WebPage):
            item._add_webpage(self._story)
        elif isinstance(item, Map):
            item._add_webmap(self._story)
        elif isinstance(item, Text):
            item._add_text()
