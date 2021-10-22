import json
import os
import PIL.Image
import mimetypes
from typing import Optional, Union
import uuid
import time
from urllib.parse import urlparse
from arcgis.gis import Item


class Image(object):
    """
    Class representing an image from a url or file
    """

    def __init__(
        self, path: str = None,
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
    def _add_image(self, story, caption, alt_text, display):
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
        # Update the resource
        story._remove_resource(resource_id)
        story._add_resource(self._path)


###############################################################################################################
class Video(object):
    """
    Class representing a video from a url or file
    """

    def __init__(
        self, path: str = None,
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
    def _add_video(self, story, caption, alt_text, display):
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
            "config": {"size": display,},
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
        # Update the resource
        story._remove_resource(resource_id)
        story._add_resource(self._path)


###############################################################################################################
class Audio(object):
    """
    Class representing an audio from a url or file

    """

    def __init__(
        self, path: str = None,
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
    def _add_audio(self, story, caption, alt_text, display):
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
            "config": {"size": display,},
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
        resource_node_id = story.properties["nodes"][node_id]["data"]["audio"]
        # UPDATE RESOURCE
        resource_id = story.properties["resources"][resource_node_id]["data"][
            "resourceId"
        ]
        story.properties["resources"][resource_node_id]["data"][
            "resourceId"
        ] = os.path.basename(os.path.normpath(self._path))
        # Update the resource
        story._remove_resource(resource_id)
        story._add_resource(self._path)


###############################################################################################################
class WebPage(object):
    """
    Class representing a hyperlink from a url
    """

    def __init__(
        self, path: str = None,
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
    def _add_webpage(self, story, caption, alt_text):

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

    # ----------------------------------------------------------------------
    def _add_text(self, story):

        story.properties["nodes"][self._node] = {
            "type": "text",
            "data": {"type": self._style, "text": self._text,},
        }
        if self._color is not None:
            story.properties["nodes"][self._node]["data"]["customTextColors"] = [
                self._color
            ]

    # ----------------------------------------------------------------------
    def _update_text(self, story):
        """
        TODO: Implement update text for this method
        """


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


###############################################################################################################
class Map(object):
    """
    Class representing a webmap or webscene for the story

    """

    def __init__(
        self,
        item: Item,
        caption: Optional[str] = None,
        alt_text: Optional[str] = None,
        display: str = "float",
        show_legend: bool = False,
        extent: Optional[dict] = None,
        center: Optional[list] = None,
        zoom: Optional[int] = None,
        viewpoint: Optional[dict] = None,
        layer_visibility: Optional[list] = None,
    ):
        """

        =================       ====================================================================
        **Argument**            **Description**
        -----------------       --------------------------------------------------------------------
        item                    An Item of type Web Map to add to the story map.
        -----------------       --------------------------------------------------------------------
        caption                 Optional string. The caption of the section.
        -----------------       --------------------------------------------------------------------
        alt_text                Optional string. Specifies an alternate text for an image.
        -----------------       --------------------------------------------------------------------
        display                 Optional string. The image display properties.
        -----------------       --------------------------------------------------------------------
        position                Optional int. Will position the element in the story list.
        -----------------       --------------------------------------------------------------------
        show_legend             Optional Boolean. If True, map legend is shown. The default is False.
        -----------------       --------------------------------------------------------------------
        extent                  Optional Dictionary.

                                Example:
                                extent = {
                                    "xmin": -9177882,
                                    "ymin": 4246761,
                                    "xmax": -9176720,
                                    "ymax": 4247967,
                                    "spatialReference": { "wkid": 102100 }
                                    }
        -----------------       --------------------------------------------------------------------
        center                  Optional List of two integers.

                                Example:
                                center = [-112, 38]
        -----------------       --------------------------------------------------------------------
        zoom                    Optional Integer. The zoom level of the map.
        -----------------       --------------------------------------------------------------------
        viewpoint               Optional Dictionary. Represents the current view as a Viewpoint or point
                                of observation on the view.

                                Example:
                                viewpoint = {
                                    "rotation": 0,
                                    "scale": 369785.47,
                                    "targetGeometry": {
                                        "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                                        "x": 279.71,
                                        "y": -998.98
                                    },
                                }
        -----------------       --------------------------------------------------------------------
        layer_visibility        Optional List of Dictionaries. The visibility of the layers in a webmap.

                                Syntax:

                                    [
                                    {
                                        "id" : "<layer_id>",
                                        "visibility" : "<true/false>"
                                    }
                                    ]
        =================       ====================================================================

        """
        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._resource_node = "r-" + item.id
        self._path = item
        self._caption = caption
        self._alt_text = alt_text
        self._display = display
        self._show_legend = show_legend
        self._center = center
        self._zoom = zoom
        if extent is None and "extent" in item and item.extent:
            self._extent = {
                "xmin": item.extent[0][0],
                "xmax": item.extent[1][0],
                "ymin": item.extent[0][1],
                "ymax": item.extent[1][1],
            }
        else:
            self._extent = extent

        if viewpoint is not None:
            self._viewpoint = json.dumps(viewpoint)
        else:
            self._viewpoint = None
        if layer_visibility is not None:
            self._layer_visibility = json.dumps(layer_visibility)
        elif "layers" in item:
            layer_visibility = []
            for layer in item.layers:
                layer_item = {
                    "id": layer.properties.id,
                    "title": layer.properties.name,
                    "visibility": True,
                }
                layer_visibility.append(layer_item)
            self._layer_visibility = layer_visibility
        else:
            self._layer_visibility = None

        self._type = item.type
        self._resource_id = str(int(time.time())) + "_" + item.type

    # ----------------------------------------------------------------------
    def _add_webmap(self, story):
        # Make an add resource call (NOT IMPLEMENTED ON GUI YET)
        # story._add_resource(resource_name= self._resource_id, text=json.dumps(self._path))

        # Create webmap nodes
        story.properties["nodes"][self._node] = {
            "type": "webmap",
            "data": {
                "map": self._resource_node,
                "caption": self._caption,
                "alt": self._alt_text,
                "mapLayers": self._layer_visibility,
                "extent": self._extent,
                "center": self._center,
                "zoom": self._zoom,
                "viewpoint": self._viewpoint,
                "showLegend": self._show_legend,
            },
            "config": {"size": self._display},
        }

        # Create resource node
        story.properties["resources"][self._resource_node] = {
            "type": "webmap",
            "data": {
                "extent": self._extent,
                "center": self._center,
                "zoom": self._zoom,
                "viewpoint": self._viewpoint,
                "mapLayers": self._layer_visibility,
                "itemId": self._path.id,
                "itemType": self._type,
                "type": "default",
                "showLegend": self._show_legend,
            },
        }

    # ----------------------------------------------------------------------
    def _update_map(self, node_id, story):
        # TODO: UPDATE RESOURCES and Properties.
        resource_id = story.properties["resources"][node_id]["data"]["resourceId"]


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
        ===============     ====================================================================

        """
        if item is not None:
            if not isinstance(item, Image) or not isinstance(item, Map):
                raise Exception("Swipe nodes can only accept Image or Map item type")
            # If user has created the item but not added to the story yet.
            if item._node not in story.properties["nodes"]:
                if isinstance(item, Image):
                    node, resource = item._add_image(story, caption, alt_text)
                    self.properties["nodes"][item._node] = node
                    self.properties["resources"][item._resource_node] = resource
            elif isinstance(item, Map):
                node, resource = item._add_webmap(story)
                self.properties["nodes"][item._node] = node
                self.properties["resources"][item._resource_node] = resource
            # Add to content in position wanted
            if position == "left":
                self._content["0"] = item._node
            else:
                self._content["1"] = item._node
        else:
            if caption is not None:
                self._data["caption"] = caption
            if alt_text is not None:
                self._data["alt"] = alt_text


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
        self, item: Union[Image, Video, Map, Text, WebPage], slide_number: int
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
        narrative_panel = self._story.properties["nodes"][slide]["children"][0]
        media_item = None
        if len(self._story.properties["nodes"][slide]["children"]) == 2:
            media_item = self._story.properties["nodes"][slide]["children"][1]

        # Check to see if item has been added to node properties
        if item._node not in self._story.properties["nodes"]:
            self._add_item_story(item)

        # Insert new item
        if isinstance(item, Text):
            # If item is text then update the narrative panel by removing old text and adding new
            old_text_node = narrative_panel["children"][0]
            self._story.delete(old_text_node)
            narrative_panel["children"].insert(item._node)
        else:
            # Remove current media item and add new item as media
            if media_item:
                self._story.delete(media_item)
            self._story.properties["nodes"][slide]["children"].insert(1, item._node)

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
    def list_slides(self):
        """
        List all slides and their children

        :return: 
            A list where the first item is the node id for the sidecar. Next
            items are dictionary of slides and their children.
        """
        sidecar_tree = [self._node_id]
        for slide in self._slides:
            slide = []
            narrative_panel = self._story.properties["nodes"][slide]["children"][0]
            text = self._story.properties["nodes"][narrative_panel]["children"]
            media_item = self._story.properties["nodes"][slide]["children"][1]
            slide.insert(
                {
                    "Slide: "
                    + slide: [
                        "Narrative Panel: " + narrative_panel,
                        "Text: " + text,
                        "Media Item: " + media_item,
                    ]
                }
            )
            sidecar_tree.insert(slide)
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
            node, resource = item._add_image(self._story)
            self._story.properties["nodes"][item._node] = node
            self._story.properties["resources"][item._resource_node] = resource
        elif isinstance(item, Video):
            node, resource = item._add_video(self._story)
            self._story.properties["nodes"][item._node] = node
            self._story.properties["resources"][item._resource_node] = resource
        elif isinstance(item, WebPage):
            node, resource = item._add_webpage(self._story)
            self._story.properties["nodes"][item._node] = node
        elif isinstance(item, Map):
            node, resource = item._add_webmap(self._story)
            self._story.properties["nodes"][item._node] = node
            self._story.properties["resources"][item._resource_node] = resource
        elif isinstance(item, Text):
            node, resource = item._add_text()
            self._story.properties["nodes"][item._node] = node


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
        narrative_panel = self._story.properties["nodes"][slide]["children"][0]
        media_item = self._story.properties["nodes"][slide]["children"][1]

        # Check to see if item has been added to node properties
        if item._node not in self._story.properties["nodes"]:
            self._add_item_story(item)

        # Insert new item
        if isinstance(item, Text):
            # If item is text then update the narrative panel by removing old text and adding new
            old_text_node = narrative_panel["children"][0]
            self._story.delete(old_text_node)
            narrative_panel["children"].insert(item._node)
        else:
            # Remove current media item and add new item as media
            if media_item:
                self._story.delete(media_item)
            self._story.properties["nodes"][slide]["children"].insert(1, item._node)

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
    def list_slides(self):
        """
        List all slides and their children

        :return: 
            A list where the first item is the node id for the slideshow. Next
            items are dictionary of slides and their children.
        """
        slideshow_tree = [self._node_id]
        for slide in self._slides:
            slide = []
            narrative_panel = self._story.properties["nodes"][slide]["children"][0]
            text = self._story.properties["nodes"][narrative_panel]["children"]
            media_item = self._story.properties["nodes"][slide]["children"][1]
            slide.insert(
                {
                    "Slide: "
                    + slide: [
                        "Narrative Panel: " + narrative_panel,
                        "Text: " + text,
                        "Media Item: " + media_item,
                    ]
                }
            )
            slideshow_tree.insert(slide)
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
            node, resource = item._add_image(self._story)
            self._story.properties["nodes"][item._node] = node
            self._story.properties["resources"][item._resource_node] = resource
        elif isinstance(item, Video):
            node, resource = item._add_video(self._story)
            self._story.properties["nodes"][item._node] = node
            self._story.properties["resources"][item._resource_node] = resource
        elif isinstance(item, WebPage):
            node, resource = item._add_webpage(self._story)
            self._story.properties["nodes"][item._node] = node
        elif isinstance(item, Map):
            node, resource = item._add_webmap(self._story)
            self._story.properties["nodes"][item._node] = node
            self._story.properties["resources"][item._resource_node] = resource
        elif isinstance(item, Text):
            node, resource = item._add_text()
            self._story.properties["nodes"][item._node] = node
