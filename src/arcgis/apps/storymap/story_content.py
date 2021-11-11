from __future__ import annotations
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

    def __init__(self, path: Optional[str] = None, **kwargs):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        path                    Required String. The file path to the image that will be added.
        ==================      ====================================================================

        This creates an Image item containing:
            - self._path: The image path or url
            - self._url: A boolean indicating whether the image is from a url
            - self.node: A unique id for use in the story's nodes dictionary
            - self.resource_node: A unique id for use in the story's resources dictionary
            - self._type: The type of node
            - self._story: The story the this content is associated with.
        """
        self._story = kwargs.pop("story", None)
        self._type = "image"
        self._url = False
        self.node = kwargs.pop("node_id", None)
        # If node exists in story, then create from resources and node dict.
        # If node doesn't already exist, create a new instance
        existing = self._check_node()
        if existing is True:
            self.resource_node = self._story._properties["nodes"][self.node]["data"][
                "image"
            ]
            if (
                self._story._properties["resources"][self.resource_node]["data"][
                    "provider"
                ]
                == "uri"
            ):
                self._url = True
            if self._url is True:
                self._path = self._story._properties["resources"][self.resource_node][
                    "data"
                ]["src"]
            else:
                self._path = self._story._properties["resources"][self.resource_node][
                    "data"
                ]["resourceId"]
        elif existing is False:
            self._path = path
            self.node = "n-" + uuid.uuid4().hex[0:6]
            self.resource_node = "r-" + uuid.uuid4().hex[0:6]

            # determine if url or file path
            if _parse.urlparse(self._path).scheme == "https":
                self._url = True

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get properties for the Image.

        :return:
            A dictionary depicting the node dictionary and resource
            dictionary for the image.
            If nothing is returned, make sure your content has been added
            to the story.

        ..note:
            To change various properties of the Image use the other property setters.
        """
        if self._check_node() is True:
            return {
                "node_dict": self._story._properties["nodes"][self.node],
                "resource_dict": self._story._properties["resources"][
                    self.resource_node
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
        if self._check_node() is True:
            if self._url is False:
                return self._story._properties["resources"][self.resource_node]["data"][
                    "resourceId"
                ]
            else:
                return self._story._properties["resources"][self.resource_node]["data"][
                    "src"
                ]

    # ----------------------------------------------------------------------
    @image.setter
    def image(self, path):
        if self._check_node() is True:
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
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if self._check_node() is True:
            if isinstance(caption, str):
                self._story._properties["nodes"][self.node]["data"]["caption"] = caption
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
        return self._story._properties["nodes"][self.node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        if self._check_node() is True:
            self._story._properties["nodes"][self.node]["data"]["alt"] = alt_text
            return self.alt_text

    # ----------------------------------------------------------------------
    @property
    def display(self, display):
        """
        Get/Set display for image.

        Values: "small" | "wide" | "full" | "float"
        """
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["config"]["size"]

    # ----------------------------------------------------------------------
    @display.setter
    def display(self, display):
        if self._check_node() is True:
            self._story._properties["nodes"][self.node]["config"]["size"] = display
            return self.display

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node

        :return: True if successful.
        """
        return self._story._delete(self.node, self.resource_node)

    # ----------------------------------------------------------------------
    def _add_image(self, caption=None, alt_text=None, display=None, story=None):
        self._story = story
        # Make an add resource call
        if self._url is False:
            self._story._add_resource(self._path)

        # Create image nodes
        self._story._properties["nodes"][self.node] = {
            "type": "image",
            "data": {
                "image": self.resource_node,
                "caption": caption,
                "alt": alt_text,
            },
            "config": {"size": display},
        }

        # Create resource node
        if self._url is False:
            im = _Image.open(self._path)
            w, h = im.size
            self._story._properties["resources"][self.resource_node] = {
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
            self._story._properties["resources"][self.resource_node] = {
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
        if _parse.urlparse(new_image).scheme == "https":
            # Update the height and width for the image
            data = requests.get(new_image).content
            im = _Image.open(_io.BytesIO(data))
            w, h = im.size
            self._story._properties["resources"][self.resource_node]["data"][
                "height"
            ] = h
            self._story._properties["resources"][self.resource_node]["data"][
                "width"
            ] = w

            # Update resource dictionary
            self._story._properties["resources"][self.resource_node]["data"][
                "src"
            ] = new_image
            self._story._properties["resources"][self.resource_node]["data"][
                "provider"
            ] = "uri"
        else:
            # Update the height and width for the image
            im = _Image.open(new_image)
            w, h = im.size
            self._story._properties["resources"][self.resource_node]["data"][
                "height"
            ] = h
            self._story._properties["resources"][self.resource_node]["data"][
                "width"
            ] = w

            # Update resource dictionary
            resource_id = self._story._properties["resources"][self.resource_node][
                "data"
            ]["resourceId"]
            self._story._properties["resources"][self.resource_node]["data"][
                "resourceId"
            ] = os.path.basename(os.path.normpath(new_image))
            self._story._properties["resources"][self.resource_node]["data"][
                "provider"
            ] = "item-resource"
            # Update the resource
            self._story._remove_resource(resource_id)
            self._story._add_resource(new_image)
        self._path = new_image

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._story is None:
            return False
        elif self.node is None:
            return False
        else:
            return True


###############################################################################################################
class Video(object):
    """
    Class representing a video from a url or file
    """

    def __init__(self, path: Optional[str] = None, **kwargs):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        path                    Required String. The file path or embed url to the video that will
                                be added.

                                ..note:
                                    url must be an embed url.
                                    Example: "https://www.youtube.com/embed/G6b7Kgvd0iA"

        ==================      ====================================================================
        """
        self._story = kwargs.pop("story", None)
        self._type = "video"
        self._url = False
        self.node = kwargs.pop("node_id", None)
        existing = self._check_node()
        if existing is True:
            if self._story._properties["nodes"][self.node]["type"] == "video":
                self.resource_node = self._story._properties["nodes"][self.node][
                    "data"
                ]["video"]
                self._path = self._story._properties["resources"][self.resource_node][
                    "data"
                ]["resourceId"]
            else:
                self.resource_node = None
                self._path = self._story._properties["nodes"][self.node]["data"]["url"]
                self._url = True
        else:
            self._path = path
            self.node = "n-" + uuid.uuid4().hex[0:6]
            if _parse.urlparse(path).scheme == "https":
                self._url = True
                self.resource_node = None
            else:
                self.resource_node = "r-" + uuid.uuid4().hex[0:6]

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get properties for the Video.

        :return:
            A dictionary depicting the node dictionary and resource
            dictionary for the video.
            If nothing is returned, make sure the content is part of the story.

        ..note:
            To change various properties of the Video use the other property setters.
        """
        if self._check_node() is True:
            vid_dict = {
                "node_dict": self._story._properties["nodes"][self.node],
            }
            if self.resource_node:
                vid_dict["resource_dict"] = (
                    self._story._properties["resources"][self.resource_node],
                )
            return vid_dict

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
        if self._check_node() is True:
            if self.resource_node:
                return self._story._properties["resources"][self.resource_node]["data"][
                    "resourceId"
                ]
            else:
                return self._story._properties["nodes"][self.node]["data"]["url"]

    # ----------------------------------------------------------------------
    @video.setter
    def video(self, path):
        if self._check_node() is True:
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
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if self._check_node() is True:
            if isinstance(caption, str):
                self._story._properties["nodes"][self.node]["data"]["caption"] = caption
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
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        if self._check_node() is True:
            self._story._properties["nodes"][self.node]["data"]["alt"] = alt_text
            return self.alt_text

    # ----------------------------------------------------------------------
    @property
    def display(self):
        """
        Get/Set display for the video.

        Values: “small” | “wide” | “full” | “float”

        ..note:
            Cannot change display when video is created from a url
        """
        if self._check_node() is True:
            if self._url is True:
                return self._story._properties["nodes"][self.node]["data"]["display"]
            else:
                return self._story._properties["nodes"][self.node]["config"]["size"]

    # ----------------------------------------------------------------------
    @display.setter
    def display(self, display):
        if self._check_node() is True:
            if self._url is True:
                self._story._properties["nodes"][self.node]["data"]["display"] = display
        return self.display

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node

        :return: True if successful
        """
        return self._story._delete(self.node, self.resource_node)

    # ----------------------------------------------------------------------
    def _add_video(
        self,
        caption=None,
        alt_text=None,
        display=None,
        story=None,
        node_id=None,
        resource_node=None,
    ):
        self._story = story
        if node_id:
            self.node = node_id
        if resource_node:
            self.resource_node = resource_node
        if self._url is False:
            # Make an add resource call
            self._story._add_resource(self._path)

            # Create video nodes
            self._story._properties["nodes"][self.node] = {
                "type": "video",
                "data": {
                    "video": self.resource_node,
                    "caption": caption,
                    "alt": alt_text,
                },
                "config": {
                    "size": display,
                },
            }

            # Create resource node
            self._story._properties["resources"][self.resource_node] = {
                "type": "video",
                "data": {
                    "resourceId": os.path.basename(os.path.normpath(self._path)),
                    "provider": "item-resource",
                },
            }
        else:
            self._story._properties["nodes"][self.node] = {
                "type": "embed",
                "data": {
                    "url": self._path,
                    "embedType": "video",
                    "caption": caption,
                    "alt": alt_text,
                    "display": "inline",
                    "aspectRatio": 1.778,
                    "addedAsEmbedCode": True,
                },
            }

    # ----------------------------------------------------------------------
    def _update_video(self, new_video):
        # Steps to update include setting the new path
        # The way the video node is updated depends if it
        # is a url or file path.
        # Cannot use same method as image since video url is turned into type embed.
        self._path = new_video
        if self.resource_node:
            # If resource node present, remove resource from item
            resource_id = self._story._properties["resources"][self.resource_node][
                "data"
            ]["resourceId"]
            self._story._remove_resource(resource_id)
            # Remove the resource node since should not exist for url
            del self._story._properties["resources"][self.resource_node]
        if _parse.urlparse(new_video).scheme == "https":
            self._url = True
            self.resource_node = None
            self._add_video(
                caption=self.caption,
                alt_text=self.alt_text,
                story=self._story,
                node_id=self.node,
            )
        else:
            # If the node was not a file path before, need to create resource id
            if self.resource_node is None:
                self.resource_node = "r-" + uuid.uuid4().hex[0:6]
            # display depends on self._url so get it before
            display = self.display
            self._url = False
            self._add_video(
                caption=self.caption,
                alt_text=self.alt_text,
                display=display,
                story=self._story,
                node_id=self.node,
                resource_node=self.resource_node,
            )

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._story is None:
            return False
        elif self.node is None:
            return False
        else:
            return True


###############################################################################################################
class Audio(object):
    """
    Class representing an audio from a url or file

    """

    def __init__(self, path: Optional[str] = None, **kwargs):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        path                    Required String. The file path to the image that will be added.

                                ..note:
                                    url must be an embed url.
                                    Example: "https://www.youtube.com/embed/G6b7Kgvd0iA"

        ==================      ====================================================================
        """
        # Audio cannot be added by Url at this time.
        if _parse.urlparse(path).scheme == "https":
            raise ValueError(
                "To add an audio from an embedded url, use the Embed content class."
            )

        self._story = kwargs.pop("story", None)
        self._type = "audio"
        self.node = kwargs.pop("node_id", None)
        existing = self._check_node()
        if existing is True:
            self.resource_node = self._story._properties["nodes"][self.node]["data"][
                "audio"
            ]
            self._path = self._story._properties["resources"][self.resource_node][
                "data"
            ]["resourceId"]
        else:
            self._path = path
            self.node = "n-" + uuid.uuid4().hex[0:6]
            self.resource_node = "r-" + uuid.uuid4().hex[0:6]

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get properties for the Audio.

        :return:
            A dictionary depicting the node dictionary and resource
            dictionary for the audio.
            If nothing is returned, make sure the content is part of the story.

        ..note:
            To change various properties of the Audio use the other property setters.
        """
        if self._check_node() is True:
            return {
                "node_dict": self._story._properties["nodes"][self.node],
                "resource_dict": self._story._properties["resources"][
                    self.resource_node
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
        if self._check_node() is True:
            return self._story._properties["resources"][self.resource_node]["data"][
                "resourceId"
            ]

    # ----------------------------------------------------------------------
    @audio.setter
    def audio(self, path):
        if _parse.urlparse(path).scheme == "https":
            raise ValueError(
                "To add an audio from an embedded url, use the Embed content class. Update audio with file path only."
            )
        if self._check_node() is True:
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
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if self._check_node() is True:
            if isinstance(caption, str):
                self._story._properties["nodes"][self.node]["data"]["caption"] = caption
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
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        if self._check_node() is True:
            self._story._properties["nodes"][self.node]["data"]["alt"] = alt_text
            return self.alt_text

    # ----------------------------------------------------------------------
    @property
    def display(self):
        """
        Get/Set display for audio.

        Values: "small" | "wide" | "float"
        """
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["config"]["size"]

    # ----------------------------------------------------------------------
    @display.setter
    def display(self, display):
        if self._check_node() is True:
            self._story._properties["nodes"][self.node]["config"]["size"] = display
            return self.display

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node

        :return: True if successful
        """
        return self._story._delete(self.node, self.resource_node)

    # ----------------------------------------------------------------------
    def _add_audio(
        self,
        caption="",
        alt_text="",
        display=None,
        story=None,
    ):
        self._story = story
        # Make an add resource call
        self._story._add_resource(self._path)
        # Create image nodes
        self._story._properties["nodes"][self.node] = {
            "type": "audio",
            "data": {
                "audio": self.resource_node,
                "caption": caption,
                "alt": alt_text,
            },
            "config": {"size": display},
        }

        # Create resource node
        self._story._properties["resources"][self.resource_node] = {
            "type": "audio",
            "data": {
                "resourceId": os.path.basename(os.path.normpath(self._path)),
                "provider": "item-resource",
            },
        }

    # ----------------------------------------------------------------------
    def _update_audio(self, new_audio):
        # Assign new path
        self._path = new_audio

        # Assign new resouce id, get old one to delete resource
        resource_id = self._story._properties["resources"][self.resource_node]["data"][
            "resourceId"
        ]
        self._story._properties["resources"][self.resource_node]["data"][
            "resourceId"
        ] = os.path.basename(os.path.normpath(self._path))

        # Add new resource and remove old one
        self._story._add_resource(self._path)
        self._story._remove_resource(resource_id)

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._story is None:
            return False
        elif self.node is None:
            return False
        else:
            return True


###############################################################################################################
class Embed(object):
    """
    Class representing an embedded video, audio, or webpage.
    """

    def __init__(self, path: Optional[str] = None, **kwargs):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        path                    Required String. The url that will be added as a webpage, video, or
                                audio embed into the story.
        ==================      ====================================================================
        """
        self._story = kwargs.pop("story", None)
        self._type = "embed"
        self.node = kwargs.pop("node_id", None)
        existing = self._check_node()
        if existing is True:
            self._path = self._story._properties["nodes"][self.node]["data"]["url"]
        else:
            self._path = path
            self.node = "n-" + uuid.uuid4().hex[0:6]

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get properties for the Embed.

        :return:
            A dictionary depicting the node dictionary for the embed.
            If nothing is returned, make sure the content is part of the story.

        ..note:
            To change various properties of the Embed use the other property setters.
        """
        if self._check_node() is True:
            return {
                "node_dict": self._story._properties["nodes"][self.node],
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
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["data"]["url"]

    # ----------------------------------------------------------------------
    @link.setter
    def link(self, path):
        if self._check_node() is True:
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
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if self._check_node() is True:
            if isinstance(caption, str):
                self._story._properties["nodes"][self.node]["data"]["caption"] = caption
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
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        if self._check_node() is True:
            self._story._properties["nodes"][self.node]["data"]["alt"] = alt_text
            return self.alt_text

    # ----------------------------------------------------------------------
    @property
    def display(self):
        """
        Get/Set display for embed.

        Values: "card" | "inline"
        """
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["data"]["display"]

    # ----------------------------------------------------------------------
    @display.setter
    def display(self, display):
        if self._check_node():
            self._story._properties["nodes"][self.node]["data"]["display"] = display
            return self.display

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node

        :return: True if successful.
        """
        return self._story._delete(self.node)

    # ----------------------------------------------------------------------
    def _add_link(self, caption=None, alt_text=None, display="card", story=None):
        self._story = story
        sections = _parse.urlparse(self._path)
        # Create embed nodes
        self._story._properties["nodes"][self.node] = {
            "type": "embed",
            "data": {
                "url": self._path,
                "embedType": "link",
                "title": sections.netloc,
                "description": caption,
                "providerUrl": self._path,
                "alt": alt_text,
                "display": display,
            },
        }

    # ----------------------------------------------------------------------
    def _update_link(self, new_link):
        sections = _parse.urlparse(new_link)
        self._path = new_link
        self._story._properties["nodes"][self.node]["data"]["url"] = self._path
        self._story._properties["nodes"][self.node]["data"]["title"] = sections.netloc
        self._story._properties["nodes"][self.node]["data"]["providerUrl"] = self._path

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._story is None:
            return False
        elif self.node is None:
            return False
        else:
            return True


###############################################################################################################
class Map(object):
    """
    Class representing a webmap or webscene for the story

    """

    def __init__(self, item: Optional[arcgis.gis.Item] = None, **kwargs):
        """
        =================       ====================================================================
        **Argument**            **Description**
        -----------------       --------------------------------------------------------------------
        item                    An Item of type WebMap or WebScene or a String representing the item
                                id to add to the story map.
        =================       ====================================================================

        """
        self._story = kwargs.pop("story", None)
        self._type = "webmap"
        self.node = kwargs.pop("node_id", None)
        existing = self._check_node()

        if existing:
            self.resource_node = self._story._properties["nodes"][self.node]["data"][
                "map"
            ]
            # The item id is in the resource node
            self._path = self.resource_node[2::]
            self._map_layers = self._story._properties["resources"][self.resource_node][
                "data"
            ]["mapLayers"]
            self._extent = self._story._properties["resources"][self.resource_node][
                "data"
            ]["extent"]
            self._center = self._story._properties["resources"][self.resource_node][
                "data"
            ]["center"]
            self._viewpoint = self._story._properties["resources"][self.resource_node][
                "data"
            ]["viewpoint"]
            self._type = self._story._properties["resources"][self.resource_node][
                "data"
            ]["itemType"]
        else:
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

            self.node = "n-" + uuid.uuid4().hex[0:6]
            self.resource_node = "r-" + item.id

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

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get properties for the Map.

        :return:
            A dictionary depicting the node dictionary and resource
            dictionary for the map.
            If nothing it returned, make sure the content is part of the story.

        ..note:
            To change various properties of the Map use the other property setters.
        """
        if self._check_node() is True:
            return {
                "node_dict": self._story._properties["nodes"][self.node],
                "resource_dict": self._story._properties["resources"][
                    self.resource_node
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
        if self._check_node() is True:
            return self._story._properties["resources"][self.resource_node]["data"][
                "itemId"
            ]

    # ----------------------------------------------------------------------
    @map.setter
    def map(self, map):
        if self._check_node() is True:
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
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if self._check_node() is True:
            if isinstance(caption, str):
                self._story._properties["nodes"][self.node]["data"]["caption"] = caption
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
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        if self._check_node() is True:
            self._story._properties["nodes"][self.node]["data"]["alt"] = alt_text
            return self.alt_text

    # ----------------------------------------------------------------------
    @property
    def display(self):
        """
        Get/Set the display type of the map.

        Values: "standard" | "wide" | "full" | "float"
        """
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["config"]["size"]

    # ----------------------------------------------------------------------
    @display.setter
    def display(self, display):
        if self._check_node() is True:
            self._story._properties["nodes"][self.node]["config"]["size"] = display
            return self.display

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node
        """
        return self._story._delete(self.node, self.resource_node)

    # ----------------------------------------------------------------------
    def _add_map(
        self, caption=None, alt_text=None, display=None, previous_node=None, story=None
    ):
        self._story = story
        # To change webmap, resouce id needs to change but not the previous node id
        node = previous_node if previous_node is not None else self.node

        # Create webmap nodes
        self._story._properties["nodes"][node] = {
            "type": "webmap",
            "data": {
                "map": self.resource_node,
                "caption": caption,
                "alt": alt_text,
            },
            "config": {"size": display},
        }

        # Create resource node
        self._story._properties["resources"][self.resource_node] = {
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
        del self._story._properties["resources"][self.resource_node]
        self.resource_node = new_map.resource_node

        new_map._add_map(
            caption=self.caption,
            alt_text=self.alt_text,
            display=self.display,
            previous_node=self.node,
            story=self._story,
        )

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._story is None:
            return False
        elif self.node is None:
            return False
        else:
            return True


###############################################################################################################
class Text(object):
    """
    Class representing a text

    """

    def __init__(
        self,
        text: Optional[str] = None,
        style: TextStyles = TextStyles.PARAGRAPH,
        color: str = "000",
        **kwargs,
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
        self._story = kwargs.pop("story", None)
        self._type = "text"
        self.node = kwargs.pop("node_id", None)
        existing = self._check_node()
        if existing is True:
            self._text = self._story._properties["nodes"][self.node]["data"]["text"]
            self._style = self._story._properties["nodes"][self.node]["data"]["type"]
        else:
            self.node = uuid.uuid4().hex[0:6]
            self._text = text
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
            If nothing is returned, make sure the content is part of the story.
        """
        if self._check_node() is True:
            return {
                "node_dict": self._story._properties["nodes"][self.node],
            }

    # ----------------------------------------------------------------------
    @properties.setter
    def properties(self, text):
        if self._check_node() is True:
            self._story._properties["nodes"][self.node] = text
            return self.properties

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node

        :return: True if successful.
        """
        return self._story._delete(self.node)

    # ----------------------------------------------------------------------
    def _add_text(self, story=None):
        self._story = story
        self._story._properties["nodes"][self.node] = {
            "type": "text",
            "data": {
                "type": self._style,
                "text": self._text,
            },
        }
        if self._color is not None:
            self._story._properties["nodes"][self.node]["data"]["customTextColors"] = [
                self._color
            ]

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._story is None:
            return False
        elif self.node is None:
            return False
        else:
            return True


###############################################################################################################
class Button(object):
    """
    Class representing a button
    """

    def __init__(
        self, link: Optional[str] = None, text: Optional[str] = None, **kwargs
    ):
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
        self._story = kwargs.pop("story", None)
        self._type = "button"
        self.node = kwargs.pop("node_id", None)
        existing = self._check_node()

        if existing is True:
            self._link = self._story._properties["nodes"][self.node]["data"]["link"]
            self._text = self._story._properties["nodes"][self.node]["data"]["text"]
        else:
            self.node = uuid.uuid4().hex[0:6]
            self._link = link
            self._text = text

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
            If nothing is returned, make sure the content is part of the story.
        """
        if self._check_node() is True:
            return {"node_dict": self._story._properties["nodes"][self.node]}

    # ----------------------------------------------------------------------
    @properties.setter
    def properties(self, button):
        if self._check_node() is True:
            self._story._properties["nodes"][self.node] = button
            return self.properties

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node
        """
        return self._story._delete(self.node)

    # ----------------------------------------------------------------------
    def _add_button(self, story):
        self._story = story
        self._story._properties["nodes"][self.node] = {
            "type": "button",
            "data": {"text": self._text, "link": self._link},
        }

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._story is None:
            return False
        elif self.node is None:
            return False
        else:
            return True


###############################################################################################################
class Gallery(object):
    """
    Class representing an Image Gallery from Images
    """

    def __init__(self, **kwargs):
        """
        Create an empty gallery.
        In order to add images to the gallery, use the add method in the Gallery class.
        """
        self._story = kwargs.pop("story", None)
        self._type = "gallery"
        self.node = kwargs.pop("node_id", None)
        existing = self._check_node()
        if existing is True:
            self._children = self._story._properties["nodes"][self.node]["children"]
        elif existing is False:
            self._children = []
            self.node = "n-" + uuid.uuid4().hex[0:6]

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get properties of the Gallery object

        :return:
            A dictionary depicting the node in the story.
            If nothing is returned, make sure the gallery is part of the story.
        """
        if self._check_node() is True:
            return {
                "node_dict": self._story._properties["nodes"][self.node],
            }

    # ----------------------------------------------------------------------
    @property
    def images(self):
        """
        Get/Set list of image nodes in the image gallery. Setting the lists allows the images
        to be reordered.

        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        node_list               List of node ids for the images in the gallery. Nodes must already be
                                in the gallery and this list will adjust the order of the images.

                                To add new images to the gallery use: Gallery.add_images(images)
                                To delete an image from a gallery use: Gallery.delete_image(node_id)
        ==================      ====================================================================

        :return:
            A list of node ids in order of image appearance in the gallery.
            If nothing is returned, make sure the gallery is part of the story.
        """
        if self._check_node():
            # Update incase addition or removal was made in between last check.
            self._children = self._story._properties["nodes"][self.node]["children"]
            return self._children

    # ----------------------------------------------------------------------
    @images.setter
    def images(self, node_list):
        if self._check_node():
            self._children = node_list
            self._story._properties["nodes"][self.node]["children"] = node_list
        return self.images

    # ----------------------------------------------------------------------
    @property
    def caption(self):
        """
        Get/Set the caption property for the swipe.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        caption             String. The new caption for the Gallery.
        ==================  ========================================

        :return:
            The caption that is being used.
        """
        return self._story._properties["nodes"][self.node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if isinstance(caption, str):
            self._story._properties["nodes"][self.node]["data"]["caption"] = caption
        return self.caption

    # ----------------------------------------------------------------------
    @property
    def alt_text(self):
        """
        Get/Set the alternte text property for the swipe.

        ==================  ========================================
        **Argument**        **Description**
        ------------------  ----------------------------------------
        alt_text            String. The new alt_text for the Gallery.
        ==================  ========================================

        :return:
            The alternate text that is being used.
        """
        return self._story._properties["nodes"][self.node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        self._story._properties["nodes"][self.node]["data"]["alt"] = alt_text
        return self.alt_text

    # ----------------------------------------------------------------------
    @property
    def display(self):
        """
        Get/Set the display type of the Gallery.

        Values: "jigsaw" | "square-dynamic"
        """
        if self._check_node() is True:
            return self._story._properties["nodes"][self.node]["config"]["size"]

    # ----------------------------------------------------------------------
    @display.setter
    def display(self, display):
        if self._check_node() is True:
            self._story._properties["nodes"][self.node]["config"]["size"] = display
            return self.display

    # ----------------------------------------------------------------------
    def add_images(self, images: list[Image]):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        images                  Required list of images of type Image.
        ==================      ====================================================================
        """
        if self._check_node():
            if len(self.images) == 12:
                raise Warning(
                    "Maximum amount of images permitted is 12. Use Gallery.delete(image_node) to remove images before adding."
                )
            if images is not None:
                for image in images:
                    if image.node not in self._story._properties["nodes"]:
                        image._add_image(story=self._story)
                    self._story._properties["nodes"][self.node]["children"].append(
                        image.node
                    )
        return self.images

    # ----------------------------------------------------------------------
    def delete_image(self, image: str):
        """
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        image                   Required String. The node id for the image to be removed from the gallery.
        ==================      ====================================================================
        """
        if image in self.images:
            # Remove from the gallery list
            self._story._properties["nodes"][self.node]["children"].remove(image)
            # Remove from the story
            if "image" in self._story._properties["nodes"][image]["data"]:
                resource_node = self._story._properties["nodes"][image]["data"]["image"]
            else:
                resource_node = None
            self._story._delete(image, resource_node)
        return self.images

    # ----------------------------------------------------------------------
    def _add_gallery(self, caption=None, alt_text=None, display=None, story=None):
        self._story = story

        # Create image nodes
        self._story._properties["nodes"][self.node] = {
            "type": "gallery",
            "data": {
                "galleryLayout": display if display is not None else "jigsaw",
                "caption": caption,
                "alt": alt_text,
            },
            "children": self._children,
        }

    # ----------------------------------------------------------------------
    def _check_node(self):
        if self._story is None:
            return False
        elif self.node is None:
            return False
        else:
            return True


###############################################################################################################
class Swipe(object):
    def __init__(self, story, node: str):
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
        self.node = node
        self._story = story
        self._type = "swipe"
        self._slides = self._story._properties["nodes"][self.node]["data"]["contents"]

        # Find the type of media that the swipe supports.
        # Both contents are of the same type so only need to look at one.
        media_node = self._story._properties["nodes"][self.node]["data"]["contents"][
            "0"
        ]
        self._media_type = story._properties["nodes"][media_node]["type"]

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """
        Get properties of the Swipe object

        :return:
            A dictionary depicting the node in the story.
        """
        if self._check_node() is True:
            return {
                "node_dict": self._story._properties["nodes"][self.node],
            }

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
        return self._story._properties["nodes"][self.node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if isinstance(caption, str):
            self._story._properties["nodes"][self.node]["data"]["caption"] = caption
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
        return self._story._properties["nodes"][self.node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        self._story._properties["nodes"][self.node]["data"]["alt"] = alt_text
        return self.alt_text

    # ----------------------------------------------------------------------
    def edit(
        self,
        content: Optional[Union[Image, Map]] = None,
        position: str = "right",
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
        if content.node not in self._story._properties["nodes"]:
            if isinstance(content, Image):
                content._add_image(story=self._story)
        elif isinstance(content, Map):
            content._add_map(story=self._story)
        # Add to content in position wanted
        if position == "left":
            self._story._properties["nodes"][self.node]["data"]["content"][
                "0"
            ] = content.node
        else:
            self._story._properties["nodes"][self.node]["data"]["content"][
                "1"
            ] = content.node

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Delete the node

        :return: True if successful.
        """
        return self._story._delete(self.node)


###############################################################################################################
class Sidecar(object):
    def __init__(self, story, node: str):
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
        self.node = node
        self._type = story._properties["nodes"][node]["data"]["type"]
        if self._type != "sidecar":
            raise Exception("This node is not of type sidecar.")
        self._subtype = story._properties["nodes"][node]["data"]["subtype"]
        self._slides = story._properties["nodes"][node]["children"]

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
        return self._story._properties["nodes"][self.node]["data"]["caption"]

    # ----------------------------------------------------------------------
    @caption.setter
    def caption(self, caption):
        if isinstance(caption, str):
            self._story._properties["nodes"][self.node]["data"]["caption"] = caption
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
        return self._story._properties["nodes"][self.node]["data"]["alt"]

    # ----------------------------------------------------------------------
    @alt_text.setter
    def alt_text(self, alt_text):
        self._story._properties["nodes"][self.node]["data"]["alt"] = alt_text
        return self.alt_text

    # ----------------------------------------------------------------------
    def edit(
        self,
        content: Union[Image, Video, Map, Text, Embed],
        slide_number: int,
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
        slide_node = self._story._properties["nodes"][slide]
        narrative_panel = slide_node["children"][0]
        media_item = None
        if len(slide_node["children"]) == 2:
            media_item = slide_node["children"][1]

        # Check to see if content has been added to node properties
        if content.node not in self._story._properties["nodes"]:
            self._add_item_story(content)

        # Insert new content
        if isinstance(content, Text):
            # If content is text then update the narrative panel by removing old text and adding new
            old_text_node = narrative_panel["children"][0]
            narrative_panel["children"].pop(0)
            self._story._delete(old_text_node)
            narrative_panel["children"].insert(0, content.node)
        else:
            # Remove current media content and add new content as media
            if media_item:
                self._story._delete(media_item)
                slide_node["children"].pop(1)
            slide_node["children"].insert(1, content.node)

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
        sidecar_tree = [self.node]
        for slide in self._slides:
            narrative_panel = self._story._properties["nodes"][slide]["children"][0]
            text = self._story._properties["nodes"][narrative_panel]["children"]
            media_item = self._story._properties["nodes"][slide]["children"][1]
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
        return self._story._delete(self.node)

    # ----------------------------------------------------------------------
    def _remove_associated(self, slide):
        # Remove narrative panel and text associated
        narrative_panel = self._story._properties["nodes"][slide]["children"][0]
        self._story._delete(narrative_panel["children"][0])
        self._story._delete(narrative_panel)
        # Remove media item
        media_item = self._story._properties["nodes"][slide]["children"][1]
        self._story._delete(media_item)

    # ----------------------------------------------------------------------
    def _add_item_story(self, content):
        if isinstance(content, Image):
            content._add_image(story=self._story)
        elif isinstance(content, Video):
            content._add_video(story=self._story)
        elif isinstance(content, Embed):
            content._add_link(story=self._story)
        elif isinstance(content, Map):
            content._add_map(story=self._story)
        elif isinstance(content, Text):
            content._add_text(story=self._story)


###############################################################################################################
