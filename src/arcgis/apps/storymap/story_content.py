import json
import PIL.Image
from enum import Enum
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
        self,
        path: str = None,
        caption: Optional[str] = None,
        alt_text: Optional[str] = None,
        display: str = "float",
    ):
        self._path = path
        self._caption = caption
        self._alt_text = alt_text
        self._display = display
        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._resource_node = "r-" + uuid.uuid4().hex[0:6]

        mt = mimetypes.guess_type(path)[0].lower()
        self._ext_type = mt.split("/")[1]
        self._resource_id = str(int(time.time())) + "." + self._ext_type

    # ----------------------------------------------------------------------
    def _add_image(self):

        # Create image nodes
        node = {
            "type": "image",
            "data": {
                "image": self._resource_node,
                "caption": self._caption,
                "alt": self._alt_text,
            },
            "config": {"size": self._display},
        }

        im = PIL.Image.open(self._path)
        w, h = im.size
        # Create resource node
        resource = {
            "type": "image",
            "data": {
                "resourceId": self._resource_id,
                "provider": "item-resource",
                "height": h,
                "width": w,
            },
        }

        return node, resource

    def _update_image(self, node_id, story):
        node_dict = story.properties["nodes"][node_id]


###############################################################################################################
class Video(object):
    """
    Class representing a video from a url or file
    """

    def __init__(
        self,
        path: str = None,
        caption: Optional[str] = None,
        alt_text: Optional[str] = None,
        display: str = "float",
    ):
        self._path = path
        self._caption = caption
        self._alt_text = alt_text
        self._display = display
        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._resource_node = "r-" + uuid.uuid4().hex[0:6]

        mt = mimetypes.guess_type(path)[0].lower()
        self._ext_type = mt.split("/")[1]
        self._resource_id = str(int(time.time())) + "." + self._ext_type

    # ----------------------------------------------------------------------
    def _add_video(self):

        # Create image nodes
        node = {
            "type": "video",
            "data": {
                "video": self._resource_node,
                "caption": self._caption,
                "alt": self._alt_text,
            },
            "config": {"size": self._display,},
        }

        # Create resource node
        resource = {
            "type": "video",
            "data": {"resourceId": self._resource_id, "provider": "item-resource",},
        }

        return node, resource


###############################################################################################################
class Audio(object):
    """
    Class representing an audio from a url or file
    """

    def __init__(
        self,
        path: str = None,
        caption: Optional[str] = None,
        alt_text: Optional[str] = None,
        display: str = "float",
    ):
        self._path = path
        self._caption = caption
        self._alt_text = alt_text
        self._display = display
        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._resource_node = "r-" + uuid.uuid4().hex[0:6]

        mt = mimetypes.guess_type(path)[0].lower()
        self._ext_type = mt.split("/")[1]
        self._resource_id = str(int(time.time())) + "." + self._ext_type

    # ----------------------------------------------------------------------
    def _add_audio(self):

        # Create image nodes
        node = {
            "type": "audio",
            "data": {
                "video": self._resource_node,
                "caption": self._caption,
                "alt": self._alt_text,
            },
            "config": {"size": self._display,},
        }

        # Create resource node
        resource = {
            "type": "audio",
            "data": {"resourceId": self._resource_id, "provider": "item-resource"},
        }

        return node, resource


###############################################################################################################
class WebPage(object):
    """
    Class representing a hyperlink from a url
    """

    def __init__(
        self,
        path: str = None,
        caption: Optional[str] = None,
        alt_text: Optional[str] = None,
    ):
        self._path = path
        self._caption = caption
        self._alt_text = alt_text
        self._node = "n-" + uuid.uuid4().hex[0:6]

    # ----------------------------------------------------------------------
    def _add_webpage(self):

        sections = urlparse(self._path)

        # Create embed nodes
        node = {
            "type": "embed",
            "data": {
                "url": self._path,
                "embedType": "link",
                "title": sections.netloc,
                "description": self._caption,
                "providerUrl": self._path,
                "alt": self._alt_text,
                "display": "card",
            },
        }

        resource = None
        return node, resource


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

                                String can contain the following tags for text formatting:
                                <strong>,<em>,<a href="{link}" rel="noopener noreferer” target=”_blank”

                                Example:
                                    "Paragraph with <strong>bold</strong>,
                                    <em>italic</em> and
                                    <a href=\"https://www.google.com\" rel=\"noopener noreferrer\"
                                    target=\"_blank\">hyperlink</a> and a
                                    <span class=\"sm-text-color-080\">custom color</span>"
        ------------------      --------------------------------------------------------------------
        type                    Optional String. There are 6 different types of text that can be
                                added to a story.

                                Values: 'paragraph' | 'heading' | 'subheading' | 'numbered-list' |
                                        'bullet-list' | 'quote'

                                ..note:
                                    To make text withing these types bold, italic, or hyperlink the
                                    text parameter must include these.

        ------------------      --------------------------------------------------------------------
        custom_color            Optional String. The hex color value without the #.
                                Only available when type is either 'paragraph', 'bullet-list', or
                                'numbered-list'.

                                Ex: custom_color = "080"
        ==================      ====================================================================

        """
        self._node = uuid.uuid4().hex[0:6]
        self._text = text
        self._style = style
        self._color = color

    def _add_text(self):
        node = {
            "type": "text",
            "data": {"type": self._style, "text": self._text,},
        }

        resource = None
        return node, resource


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

    def _add_button(self):
        node = {
            "type": "button",
            "data": {"text": self._text, "link": self._link},
        }

        resource = None

        return node, resource


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

    def _add_webmap(self):

        # Create webmap nodes
        node = {
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
        resource = {
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

        return node, resource


###############################################################################################################
class Theme(Enum):
    """
    Story Map has various themes that can be used
    """
