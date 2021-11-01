from enum import Enum
from typing import Optional, Union
import uuid
from arcgis.auth.tools import LazyLoader

arcgis = LazyLoader("arcgis")
urllib3 = LazyLoader("urllib3")
requests = LazyLoader("requests")
mimetypes = LazyLoader("mimetypes")
os = LazyLoader("os")
_Image = LazyLoader("PIL.Image")
_io = LazyLoader("io")
_parse = LazyLoader("urllib.parse")


class TextStyles(Enum):
    """
    Represents the Supported Text Styles Type Enumerations.
    Example: Text(text="foo", style=TextStyles.HEADING)
    """

    PARAGRAPH = "paragraph"
    LARGEPARAGRAPH = "large-paragraph"
    BULLETLIST = "bullet-list"
    NUMBERLIST = "numbered-list"
    HEADING = "h2"
    SUBHEADING = "h3"
    QUOTE = "quote"


###############################################################################################################
class Image(object):
    """
    Class representing an image from a url or file
    """

    def __init__(self, path: str, story):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        path                    Required String. The file path to the image that will be added.
        ------------------      --------------------------------------------------------------------
        story                   Required StoryMap. The story map the image is/will be a part of.
        ==================      ====================================================================

        This creates an Image item containing:
            - self._path: The image path or url
            - self._url: A boolean indicating whether the image is from a url
            - self._node: A unique id for use in the story's nodes dictionary
            - self._resource_node: A unique id for use in the story's resources dictionary
            - self._type: The type of node and it's extension
            - self._story: The story the this content is associated with.
        """

        self._path = path
        self._url = False
        # assign ids
        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._resource_node = "r-" + uuid.uuid4().hex[0:6]
        type = mimetypes.guess_type(path)[0]
        if type is None:
            http = urllib3.PoolManager()
            response = http.request("GET", path)
            type = response.headers["Content-Type"]
            self._url = True
        self._type = type.split("/")
        self._story = story

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get properties for the Image.

        :return:
            A dictionary depicting the node dictionary and resource
            dictionary for the image.

        ..note:
            To change various properties of the Image use the other property setters.
        """
        if self._check_node:
            return {
                "node_dict": self._story.properties["nodes"][self._node],
                "resource_dict": self._story.properties["resources"][
                    self._resource_node
                ],
            }

    # ----------------------------------------------------------------------
    @property
    def image(self):
        """
        Get/Set the image property.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        image               String. The new image path or url for the Image.
        ==================  ========================================

        :return:
            The image that is being used.
        """
        if self._check_node:
            return self._story.properties["resources"][self._resource_node]["data"][
                "resourceId"
            ]

    # ----------------------------------------------------------------------
    @image.setter
    def image(self, path):
        if self._check_node:
            self._update_image(path)
            return self.image

    # ----------------------------------------------------------------------
    @property
    def caption(self):
        """
        Get/Set the caption property for the image.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        caption             String. The new caption for the Image.
        ==================  ========================================

        :return:
            The caption that is being used.
        """
        if self._check_node:
            return self._story.properties["nodes"][self._node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if self._check_node:
            if isinstance(caption, str):
                self._story.properties["nodes"][self._node]["data"]["caption"] = caption
            return self.caption

    # ----------------------------------------------------------------------
    @property
    def alt_text(self):
        """
        Get/Set the alternte text property for the image.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        alt_text            String. The new alt_text for the Image.
        ==================  ========================================

        :return:
            The alternate text that is being used.
        """
        return self._story.properties["nodes"][self._node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        if self._check_node:
            self._story.properties["nodes"][self._node]["data"]["alt"] = alt_text
            return self.alt_text

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node

        :return: True if successful.
        """
        return self._story._delete(self._node, self._resource_node)

    # ----------------------------------------------------------------------
    def _add_image(self, caption=None, alt_text=None, display=None):
        # Make an add resource call
        if self._url is False:
            self._story._add_resource(self._path)

        # Create image nodes
        self._story.properties["nodes"][self._node] = {
            "type": "image",
            "data": {
                "image": self._resource_node,
                "caption": caption,
                "alt": alt_text,
            },
            "config": {"size": display},
        }

        # Create resource node
        if self._url is False:
            im = _Image.open(self._path)
            w, h = im.size
            self._story.properties["resources"][self._resource_node] = {
                "type": "image",
                "data": {
                    "resourceId": os.path.basename(os.path.normpath(self._path)),
                    "provider": "item-resource",
                    "height": h,
                    "width": w,
                },
            }
        else:
            data = requests.get(self._path).content
            im = _Image.open(_io.BytesIO(data))
            w, h = im.size
            self._story.properties["resources"][self._resource_node] = {
                "type": "image",
                "data": {
                    "src": self._path,
                    "provider": "uri",
                    "height": h,
                    "width": w,
                },
            }

    # ----------------------------------------------------------------------
    def _update_image(self, new_image):
        # Check if new_image is url or path
        if _parse.urlparse(new_image).scheme != "":
            # Update the height and width for the image
            data = requests.get(new_image).content
            im = _Image.open(_io.BytesIO(data))
            w, h = im.size
            self._resource_node["data"]["height"] = h
            self._resource_node["data"]["width"] = w

            # Update resource dictionary
            self._resource_node["data"]["src"] = new_image
            self._resource_node["data"]["provider"] = "uri"
        else:
            # Update the height and width for the image
            im = _Image.open(new_image)
            w, h = im.size
            self._resource_node["data"]["height"] = h
            self._resource_node["data"]["width"] = w

            # Update resource dictionary
            resource_id = self._resource_node["data"]["resourceId"]
            self._resource_node["data"]["resourceId"] = os.path.basename(
                os.path.normpath(new_image)
            )
            self._resource_node["data"]["provider"] = "item-resource"
            # Update the resource
            self._story._remove_resource(resource_id)
            self._story._add_resource(new_image)

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._node in self._story.properties["nodes"]:
            return True
        else:
            raise Warning("Image must be added to story before making changes.")


###############################################################################################################
class Video(object):
    """
    Class representing a video from a url or file
    """

    def __init__(self, path: str, story):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        path                    Required String. The file path to the video that will be added.
        ------------------      --------------------------------------------------------------------
        story                   Required StoryMap. The story map the image is/will be a part of.
        ==================      ====================================================================
        """
        self._path = path

        # assign ids
        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._resource_node = "r-" + uuid.uuid4().hex[0:6]

        mt = mimetypes.guess_type(path)[0].lower()
        self._type = mt.split("/")
        self._story = story

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get properties for the Video.

        :return:
            A dictionary depicting the node dictionary and resource
            dictionary for the video.

        ..note:
            To change various properties of the Video use the other property setters.
        """
        if self._check_node:
            return {
                "node_dict": self._story.properties["nodes"][self._node],
                "resource_dict": self._story.properties["resources"][
                    self._resource_node
                ],
            }

    # ----------------------------------------------------------------------
    @property
    def video(self):
        """
        Get/Set the video property.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        video               String. The new video path for the Video.
        ==================  ========================================

        :return:
            The video that is being used.
        """
        if self._check_node:
            return self._story.properties["resources"][self._resource_node]["data"][
                "resourceId"
            ]

    # ----------------------------------------------------------------------
    @video.setter
    def video(self, path):
        if self._check_node:
            self._update_video(path)
            return self.video

    # ----------------------------------------------------------------------
    @property
    def caption(self):
        """
        Get/Set the caption property for the video.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        caption             String. The new caption for the Video.
        ==================  ========================================

        :return:
            The caption that is being used.
        """
        if self._check_node:
            return self._story.properties["nodes"][self._node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if self._check_node:
            if isinstance(caption, str):
                self._story.properties["nodes"][self._node]["data"]["caption"] = caption
            return self.caption

    # ----------------------------------------------------------------------
    @property
    def alt_text(self):
        """
        Get/Set the alternte text property for the video.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        alt_text            String. The new alt_text for the Video.
        ==================  ========================================

        :return:
            The alternate text that is being used.
        """
        if self._check_node:
            return self._story.properties["nodes"][self._node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        if self._check_node:
            self._story.properties["nodes"][self._node]["data"]["alt"] = alt_text
            return self.alt_text

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node

        :return: True if successful
        """
        return self._story._delete(self._node, self._resource_node)

    # ----------------------------------------------------------------------
    def _add_video(self, caption=None, alt_text=None, display=None):
        # Make an add resource call
        self._story._add_resource(self._path)

        # Create video nodes
        self._story.properties["nodes"][self._node] = {
            "type": "video",
            "data": {
                "video": self._resource_node,
                "caption": caption,
                "alt": alt_text,
            },
            "config": {"size": display,},
        }

        # Create resource node
        self._story.properties["resources"][self._resource_node] = {
            "type": "video",
            "data": {
                "resourceId": os.path.basename(os.path.normpath(self._path)),
                "provider": "item-resource",
            },
        }

    # ----------------------------------------------------------------------
    def _update_video(self, new_video):
        # Update resource dictionary
        resource_id = self._resource_node["data"]["resourceId"]
        self._resource_node["data"]["resourceId"] = os.path.basename(
            os.path.normpath(new_video)
        )

        # Update the resource
        self._story._remove_resource(resource_id)
        self._story._add_resource(new_video)

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._node in self._story.properties["nodes"]:
            return True
        else:
            raise Warning("Video must be added to story before making changes.")


###############################################################################################################
class Audio(object):
    """
    Class representing an audio from a url or file

    """

    def __init__(self, path: str, story):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        path                    Required String. The file path to the image that will be added.
        ------------------      --------------------------------------------------------------------
        story                   Required StoryMap. The story map the image is/will be a part of.
        ==================      ====================================================================
        """

        self._path = path

        # assign ids
        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._resource_node = "r-" + uuid.uuid4().hex[0:6]

        self._story = story

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get properties for the Audio.

        :return:
            A dictionary depicting the node dictionary and resource
            dictionary for the audio.

        ..note:
            To change various properties of the Audio use the other property setters.
        """
        if self._check_node:
            return {
                "node_dict": self._story.properties["nodes"][self._node],
                "resource_dict": self._story.properties["resources"][
                    self._resource_node
                ],
            }

    # ----------------------------------------------------------------------
    @property
    def audio(self):
        """
        Get/Set the audio property.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        audio               String. The new audio path for the Audio.
        ==================  ========================================

        :return:
            The audio that is being used.
        """
        if self._check_node:
            return self._story.properties["resources"][self._resource_node]["data"][
                "resourceId"
            ]

    # ----------------------------------------------------------------------
    @audio.setter
    def audio(self, path):
        if self._check_node:
            self._update_audio(path)
            return self.audio

    # ----------------------------------------------------------------------
    @property
    def caption(self):
        """
        Get/Set the caption property for the audio.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        caption             String. The new caption for the Audio.
        ==================  ========================================

        :return:
            The caption that is being used.
        """
        if self._check_node:
            return self._story.properties["nodes"][self._node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if self._check_node:
            if isinstance(caption, str):
                self._story.properties["nodes"][self._node]["data"]["caption"] = caption
            return self.caption

    # ----------------------------------------------------------------------
    @property
    def alt_text(self):
        """
        Get/Set the alternte text property for the audio.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        alt_text            String. The new alt_text for the Audio.
        ==================  ========================================

        :return:
            The alternate text that is being used.
        """
        if self._check_node:
            return self._story.properties["nodes"][self._node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        if self._check_node:
            self._story.properties["nodes"][self._node]["data"]["alt"] = alt_text
            return self.alt_text

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node

        :return: True if successful
        """
        return self._story._delete(self._node, self._resource_node)

    # ----------------------------------------------------------------------
    def _add_audio(self, caption=None, alt_text=None, display=None):
        # Make an add resource call
        self._story._add_resource(self._path)

        # Create image nodes
        self._story.properties["nodes"][self._node] = {
            "type": "audio",
            "data": {
                "audio": self._resource_node,
                "caption": caption,
                "alt": alt_text,
            },
            "config": {"size": display},
        }

        # Create resource node
        self._story.properties["resources"][self._resource_node] = {
            "type": "audio",
            "data": {
                "resourceId": os.path.basename(os.path.normpath(self._path)),
                "provider": "item-resource",
            },
        }

    # ----------------------------------------------------------------------
    def _update_audio(self, new_audio):
        # Update resource dictionary
        resource_id = self._resource_node["data"]["resourceId"]
        self._resource_node["data"]["resourceId"] = os.path.basename(
            os.path.normpath(new_audio)
        )

        # Update the resource
        self._story._remove_resource(resource_id)
        self._story._add_resource(new_audio)

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._node in self._story.properties["nodes"]:
            return True
        else:
            raise Warning("Audio must be added to story before making changes.")


###############################################################################################################
class Embed(object):
    """
    Class representing an embedded video, audio, or webpage.
    """

    def __init__(self, path: str, story):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        path                    Required String. The url that will be added as a webpage, video, or
                                audio embed into the story.
        ------------------      --------------------------------------------------------------------
        story                   Required StoryMap. The story map the image is/will be a part of.
        ==================      ====================================================================
        """
        self._path = path
        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._story = story

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get properties for the Embed.

        :return:
            A dictionary depicting the node dictionary for the embed.

        ..note:
            To change various properties of the Embed use the other property setters.
        """
        if self._check_node:
            return {
                "node_dict": self._story.properties["nodes"][self._node],
            }

    # ----------------------------------------------------------------------
    @property
    def link(self):
        """
        Get/Set the link property.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        link                String. The new url for the Embed.
        ==================  ========================================

        :return:
            The embed that is being used.
        """
        if self._check_node:
            return self._story.properties["nodes"][self._node]["data"]["url"]

    # ----------------------------------------------------------------------
    @link.setter
    def link(self, path):
        if self._check_node:
            self._update_link(path)
            return self.link

    # ----------------------------------------------------------------------
    @property
    def caption(self):
        """
        Get/Set the caption property for the webpage.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        caption             String. The new caption for the Embed.
        ==================  ========================================

        :return:
            The caption that is being used.
        """
        if self._check_node:
            return self._story.properties["nodes"][self._node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if self._check_node:
            if isinstance(caption, str):
                self._story.properties["nodes"][self._node]["data"]["caption"] = caption
            return self.caption

    # ----------------------------------------------------------------------
    @property
    def alt_text(self):
        """
        Get/Set the alternte text property for the embed.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        alt_text            String. The new alt_text for the Embed.
        ==================  ========================================

        :return:
            The alternate text that is being used.
        """
        if self._check_node:
            return self._story.properties["nodes"][self._node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        if self._check_node:
            self._story.properties["nodes"][self._node]["data"]["alt"] = alt_text
            return self.alt_text

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node

        :return: True if successful.
        """
        return self._story._delete(self._node)

    # ----------------------------------------------------------------------
    def _add_link(self, caption=None, alt_text=None):
        sections = _parse.urlparse(self._path)
        # Create embed nodes
        self._story.properties["nodes"][self._node] = {
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
    def _update_link(self, new_link):
        sections = _parse.urlparse(new_link)
        self._path = new_link
        self._story.properties["nodes"][self._node]["data"]["url"] = self._path
        self._story.properties["nodes"][self._node]["data"]["title"] = sections.netloc
        self._story.properties["nodes"][self._node]["data"]["providerUrl"] = self._path

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._node in self._story.properties["nodes"]:
            return True
        else:
            raise Warning("Webpage must be added to story before making changes.")


###############################################################################################################
class Map(object):
    """
    Class representing a webmap or webscene for the story

    """

    def __init__(self, item: arcgis.gis.Item, story):
        """
        =================       ====================================================================
        **Argument**            **Description**
        -----------------       --------------------------------------------------------------------
        item                    An Item of type WebMap or WebScene or a String representing the item
                                id to add to the story map.
        ------------------      --------------------------------------------------------------------
        story                   Required StoryMap. The story map the image is/will be a part of.
        =================       ====================================================================

        """

        # If string id get the item
        if isinstance(item, str):
            item = arcgis.env.active_gis.content.get(item)

        # Create map object to extract properties
        if isinstance(item, arcgis.gis.Item):
            if item.type == "Web Map":
                map_item = arcgis.mapping.WebMap(item)
            elif item.type == "Web Scene":
                map_item = arcgis.mapping.WebScene(item)
            else:
                raise ValueError("Item must be of Type Webmap or Web Scene")

        self._node = "n-" + uuid.uuid4().hex[0:6]
        self._resource_node = "r-" + item.id

        # Assign properties
        self._path = item
        if len(map_item._mapview.center) > 0:
            self._center = map_item._mapview.center
        else:
            self._center = None
        if len(map_item._mapview.extent) > 0:
            self._extent = map_item._mapview.extent
        else:
            self._extent = None
        self._viewpoint = None
        layers = []
        # Create layer dictionary:
        for layer in map_item.layers:
            layer_props = {}
            layer_props["id"] = layer["id"]
            layer_props["title"] = layer["title"]
            layer_props["visible"] = layer["visibility"]
            layers.append(layer_props)
        self._map_layers = layers
        self._type = item.type
        self._story = story

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get properties for the Map.

        :return:
            A dictionary depicting the node dictionary and resource
            dictionary for the map.

        ..note:
            To change various properties of the Map use the other property setters.
        """
        if self._check_node:
            return {
                "node_dict": self._story.properties["nodes"][self._node],
                "resource_dict": self._story.properties["resources"][
                    self._resource_node
                ],
            }

    # ----------------------------------------------------------------------
    @property
    def map(self):
        """
        Get/Set the map property.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        map                 One of three choices:
                            - String: item id for an Item of type 'webmap'
                            or 'webscene'.
                            - The Item itself.
                            - An instance of Map that has not been added
                            to the story.
        ==================  ========================================

        :return:
            The item id for the map that is being used.
        """
        if self._check_node:
            return self._story.properties["resources"][self._resource_node]["data"][
                "itemId"
            ]

    # ----------------------------------------------------------------------
    @map.setter
    def map(self, map):
        if self._check_node:
            if not isinstance(map, Map):
                map = Map(map)
            self._update_map(map)
            return self.map

    # ----------------------------------------------------------------------
    @property
    def caption(self):
        """
        Get/Set the caption property for the map.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        caption             String. The new caption for the Map.
        ==================  ========================================

        :return:
            The caption that is being used.
        """
        if self._check_node:
            return self._story.properties["nodes"][self._node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if self._check_node:
            if isinstance(caption, str):
                self._story.properties["nodes"][self._node]["data"]["caption"] = caption
            return self.caption

    # ----------------------------------------------------------------------
    @property
    def alt_text(self):
        """
        Get/Set the alternte text property for the map.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        alt_text            String. The new alt_text for the Map.
        ==================  ========================================

        :return:
            The alternate text that is being used.
        """
        if self._check_node:
            return self._story.properties["nodes"][self._node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        if self._check_node:
            self._story.properties["nodes"][self._node]["data"]["alt"] = alt_text
            return self.alt_text

    # ----------------------------------------------------------------------
    @property
    def display(self):
        """
        Get the display type of the map.
        """
        if self._check_node:
            return self._story.properties["nodes"][self._node]["config"]["size"]

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node
        """
        return self._story._delete(self._node, self._resource_node)

    # ----------------------------------------------------------------------
    def _add_map(self, caption=None, alt_text=None, display=None, previous_node=None):

        # To change webmap, resouce id needs to change but not the previous node id
        node = previous_node if previous_node is not None else self._node

        # Create webmap nodes
        self._story.properties["nodes"][node] = {
            "type": "webmap",
            "data": {"map": self._resource_node, "caption": caption, "alt": alt_text,},
            "config": {"size": display},
        }

        # Create resource node
        self._story.properties["resources"][self._resource_node] = {
            "type": "webmap",
            "data": {
                "extent": self._extent,
                "center": self._center,
                "zoom": 2,
                "mapLayers": self._map_layers,
                "viewpoint": self._viewpoint,
                "itemId": self._path.id,
                "itemType": self._type,
                "type": "default",
            },
        }

    # ----------------------------------------------------------------------
    def _update_map(self, new_map):
        # Previous node stays the same but old resource is deleted
        # Resource node gets updated since item changes
        del self._story.properties["resources"][self._resource_node]
        self._resource_node = new_map._resource_node

        new_map._add_map(
            caption=self.caption,
            alt_text=self.alt_text,
            display=self.display,
            previous_node=self._node,
        )

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._node in self._story.properties["nodes"]:
            return True
        else:
            raise Warning("Map must be added to story before making changes.")


###############################################################################################################
class Text(object):
    """
    Class representing a text

    """

    def __init__(
        self,
        story,
        text: str,
        style: TextStyles = TextStyles.PARAGRAPH,
        color: str = "000",
    ):
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
        story                   Required StoryMap. The story map the image is/will be a part of.
        ------------------      --------------------------------------------------------------------
        style                   Optional TextStyles type. There are 7 different styles of text that can be
                                added to a story.

                                Values: PARAGRPAH | LARGEPARAGRAPH | NUMBERLIST | BULLETLIST |
                                        HEADING | SUBHEADING | QUOTE

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
        self._story = story
        if isinstance(style, TextStyles):
            self._style = style.value

        # Color only applies certain styles
        if self._style in [
            "paragraph",
            "large-paragraph",
            "bullet-list",
            "numbered-list",
        ]:
            self._color = color
        else:
            self._color = None

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get/Set the properties for the text.

        ==================  ==================================================
        **Argument**        **Description**
        ------------------  --------------------------------------------------
        text                Dictionary. Holds new values for the text
                            node.

                            Must resemble this structure:
                            {
                                "type": "text",
                                "data": {
                                    "type": <value of TextStyles Class>,
                                    "text": <text>,
                                    "customTextColors": <Optional colors as an array>
                                }
                            }
        ==================  ==================================================

        :return:
            The Text dictionary for the node.
        """
        if self._check_node:
            return {
                "node_dict": self._story.properties["nodes"][self._node],
            }

    # ----------------------------------------------------------------------
    @properties.setter
    def properties(self, text):
        if self._check_node:
            self._story.properties["nodes"][self._node] = text
            return self.properties

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node

        :return: True if successful.
        """
        return self._story._delete(self._node)

    # ----------------------------------------------------------------------
    def _add_text(self):

        self._story.properties["nodes"][self._node] = {
            "type": "text",
            "data": {"type": self._style, "text": self._text,},
        }
        if self._color is not None:
            self._story.properties["nodes"][self._node]["data"]["customTextColors"] = [
                self._color
            ]

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._node in self._story.properties["nodes"]:
            return True
        else:
            raise Warning("Text must be added to story before making changes.")


###############################################################################################################
class Button(object):
    """
    Class representing a button
    """

    def __init__(self, story, link: str = None, text: str = None):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        story                   Required StoryMap. The story map the image is/will be a part of.
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
        self._story = story

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get/Set the properties for the button.

        ==================  ==================================================
        **Argument**        **Description**
        ------------------  --------------------------------------------------
        button              Dictionary. Holds new values for the button node.

                            Must resemble this structure:
                            {
                                "type": "button",
                                "data": {
                                    "text": <button text>,
                                    "link": <button link>
                                }
                            }
        ==================  ==================================================

        :return:
            The Button dictionary for the node.
        """
        if self._check_node:
            return {"node_dict": self._story.properties["nodes"][self._node]}

    # ----------------------------------------------------------------------
    @properties.setter
    def properties(self, button):
        if self._check_node:
            self._story.properties["nodes"][self._node] = button
            return self.properties

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node
        """
        return self._story._delete(self._node)

    # ----------------------------------------------------------------------
    def _add_button(self):
        self._story.properties["nodes"][self._node] = {
            "type": "button",
            "data": {"text": self._text, "link": self._link},
        }

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._node in self._story.properties["nodes"]:
            return True
        else:
            raise Warning("Button must be added to story before making changes.")


###############################################################################################################
class Swipe(object):
    def __init__(self, node: str, story):
        """
        Create an Swipe immersive object from a pre-existing immersive node.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        node                Required String. The node id for the swipe type.
        ---------------     --------------------------------------------------------------------
        story               Required StoryMap that the swipe belongs to.
        ===============     ====================================================================
        """
        self._node = node
        self._story = story
        self._type = self._data["type"]
        if self._type != "swipe":
            raise Exception("This node is not of type swipe.")
        self._slides = self._data["data"]["contents"]
        media_node = self._story.properties["nodes"][self._node]["data"]["content"]["0"]
        self._media_type = story.properties["nodes"][media_node]["type"]

    # ----------------------------------------------------------------------
    @property
    def caption(self):
        """
        Get/Set the caption property for the swipe.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        caption             String. The new caption for the Swipe.
        ==================  ========================================

        :return:
            The caption that is being used.
        """
        return self._story.properties["nodes"][self._node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if isinstance(caption, str):
            self._story.properties["nodes"][self._node]["data"]["caption"] = caption
        return self.caption

    # ----------------------------------------------------------------------
    @property
    def alt_text(self):
        """
        Get/Set the alternte text property for the swipe.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        alt_text            String. The new alt_text for the Swipe.
        ==================  ========================================

        :return:
            The alternate text that is being used.
        """
        return self._story.properties["nodes"][self._node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        self._story.properties["nodes"][self._node]["data"]["alt"] = alt_text
        return self.alt_text

    # ----------------------------------------------------------------------
    def edit(
        self, content: Optional[Union[Image, Map]] = None, position: str = "right",
    ):
        """
        Edit the media content of a Swipe item.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        content             Required story content of type: Image or Map.
        ---------------     --------------------------------------------------------------------
        position            Optional String. Either "right" or "left". Default is "right" so content
                            will be added to right panel.
        ===============     ====================================================================

        """
        # Media type must be same for right and left slide.
        if isinstance(content, Image) and self._media_type == "webmap":
            raise ValueError(
                "Media type is established as webmap. Can only accept another webmap."
            )
        if isinstance(content, Map) and self._media_type == "image":
            raise ValueError(
                "Media type is established as image. Can only accept another image."
            )
        # If user has created the content but not added to the story yet.
        if content._node not in self._story.properties["nodes"]:
            if isinstance(content, Image):
                content._add_image(self._story)
        elif isinstance(content, Map):
            content._add_map(self._story)
        # Add to content in position wanted
        if position == "left":
            self._story.properties["nodes"][self._node]["data"]["content"][
                "0"
            ] = content._node
        else:
            self._story.properties["nodes"][self._node]["data"]["content"][
                "1"
            ] = content._node

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node

        :return: True if successful.
        """
        return self._story._delete(self._node)


###############################################################################################################
class Sidecar(object):
    def __init__(self, node: str, story):
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
        self._node = node
        self._type = story.properties["nodes"][node]["data"]["type"]
        if self._type != "sidecar":
            raise Exception("This node is not of type sidecar.")
        self._subtype = node["data"]["subtype"]
        self._slides = story.properties["nodes"][node]["children"]

    # ----------------------------------------------------------------------
    @property
    def caption(self):
        """
        Get/Set the caption property for the sidecar.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        caption             String. The new caption for the Sidecar.
        ==================  ========================================

        :return:
            The caption that is being used.
        """
        return self._story.properties["nodes"][self._node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if isinstance(caption, str):
            self._story.properties["nodes"][self._node]["data"]["caption"] = caption
        return self.caption

    # ----------------------------------------------------------------------
    @property
    def alt_text(self):
        """
        Get/Set the alternte text property for the sidecar.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        alt_text            String. The new alt_text for the Sidecar.
        ==================  ========================================

        :return:
            The alternate text that is being used.
        """
        return self._story.properties["nodes"][self._node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        self._story.properties["nodes"][self._node]["data"]["alt"] = alt_text
        return self.alt_text

    # ----------------------------------------------------------------------
    def edit(
        self, content: Union[Image, Video, Map, Text, Embed], slide_number: int,
    ):
        """
        Edit slide text or media content. Media Content can be of type Image, Video, Map, or Embed.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        content             Required content to replace current media content.
                            Item type can be Image, Video, Map, Embed or Text.
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

        # Check to see if content has been added to node properties
        if content._node not in self._story.properties["nodes"]:
            self._add_item_story(content)

        # Insert new content
        if isinstance(content, Text):
            # If content is text then update the narrative panel by removing old text and adding new
            old_text_node = narrative_panel["children"][0]
            narrative_panel["children"].pop(0)
            self._story._delete(old_text_node)
            narrative_panel["children"].insert(0, content._node)
        else:
            # Remove current media content and add new content as media
            if media_item:
                self._story._delete(media_item)
                slide_node["children"].pop(1)
            slide_node["children"].insert(1, content._node)

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
        self._story._delete(slide)
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
        sidecar_tree = [self._node]
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
    def delete(self):
        """
        Delete the node

        :return: True if successful.
        """
        return self._story._delete(self._node)

    # ----------------------------------------------------------------------
    def _remove_associated(self, slide):
        # Remove narrative panel and text associated
        narrative_panel = self._story.properties["nodes"][slide]["children"][0]
        self._story._delete(narrative_panel["children"][0])
        self._story._delete(narrative_panel)
        # Remove media item
        media_item = self._story.properties["nodes"][slide]["children"][1]
        self._story._delete(media_item)

    # ----------------------------------------------------------------------
    def _add_item_story(self, content):
        if isinstance(content, Image):
            content._add_image(self._story)
        elif isinstance(content, Video):
            content._add_video(self._story)
        elif isinstance(content, Embed):
            content._add_link(self._story)
        elif isinstance(content, Map):
            content._add_map(self._story)
        elif isinstance(content, Text):
            content._add_text()


###############################################################################################################
class Slideshow(object):
    def __init__(self, node: str, story):
        """
        Create an Slideshow immersive object from a pre-existing immersive node.

        A slideshow is composed of slides. Slides are composed of two nodes: a narrative panel and a media node.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        node                Required String. The node id for the slideshow type.
        ---------------     --------------------------------------------------------------------
        story               Required StoryMap that the slideshow belongs to.
        ===============     ====================================================================
        """
        self._story = story
        self._node = node
        self._type = story.properties["nodes"][node]["data"]["type"]
        if self._type != "slideshow":
            raise Exception("This node is not of type slideshow")
        self._slides = story.properties["nodes"][node]["children"]

    # ----------------------------------------------------------------------
    @property
    def caption(self):
        """
        Get/Set the caption property for the slideshow.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        caption             String. The new caption for the Slideshow.
        ==================  ========================================

        :return:
            The caption that is being used.
        """
        return self._story.properties["nodes"][self._node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if isinstance(caption, str):
            self._story.properties["nodes"][self._node]["data"]["caption"] = caption
        return self.caption

    # ----------------------------------------------------------------------
    @property
    def alt_text(self):
        """
        Get/Set the alternte text property for the slideshow.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        alt_text            String. The new alt_text for the Slideshow.
        ==================  ========================================

        :return:
            The alternate text that is being used.
        """
        return self._story.properties["nodes"][self._node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        self._story.properties["nodes"][self._node]["data"]["alt"] = alt_text
        return self.alt_text

    # ----------------------------------------------------------------------
    def edit(self, content: Union[Image, Video, Map, Text], slide_number: int):
        """
        Edit slide text or media content. Media content can be an Image, Video, or Map.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        content             Required content to replace current media content.
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

        # Check to see if content has been added to node properties
        if content._node not in self._story.properties["nodes"]:
            self._add_item_story(content)

        # Insert new content
        if isinstance(content, Text):
            # If content is text then update the narrative panel by removing old text and adding new
            old_text_node = narrative_panel["children"][0]
            narrative_panel["children"].pop(0)
            self._story._delete(old_text_node)
            narrative_panel["children"].insert(0, content._node)
        else:
            # Remove current media content and add new content as media
            if media_item:
                self._story._delete(media_item)
                slide_node["children"].pop(1)
            slide_node["children"].insert(1, content._node)

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
        self._story._delete(slide)
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
        slideshow_tree = [self._node]
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
    def delete(self):
        """
        Delete the node

        :return: True if successful.
        """
        return self._story._delete(self._node)

    # ----------------------------------------------------------------------
    def _remove_associated(self, slide):
        # Remove narrative panel and text associated
        narrative_panel = self._story.properties["nodes"][slide]["children"][0]
        self._story._delete(narrative_panel["children"][0])
        self._story._delete(narrative_panel)
        # Remove media item
        media_item = self._story.properties["nodes"][slide]["children"][1]
        self._story._delete(media_item)

    # ----------------------------------------------------------------------
    def _add_item_story(self, content):
        if isinstance(content, Image):
            content._add_image()
        elif isinstance(content, Video):
            content._add_video()
        elif isinstance(content, Embed):
            content._add_link()
        elif isinstance(content, Map):
            content._add_map()
        elif isinstance(content, Text):
            content._add_text()
