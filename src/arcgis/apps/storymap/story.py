from enum import Enum
import os
import time
import json
import mimetypes
from typing import Optional
from arcgis import env
from arcgis.gis import GIS, Item
import uuid
import PIL.Image
from urllib.parse import urlparse


# TODO:
# Add logo
# Add credits
# Edit Text depending on type of text ('subheading' = h4 )
# Test Duplicate
# Test everything on Python Playground
# Test Navigation


class StoryMap(object):
    """ """

    _properties = None
    _gis = None
    _itemid = None
    _item = None

    def __init__(self, item: Optional[Item] = None, gis: Optional[GIS] = None):
        """
        Initializer for the Story Map Class.

        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        item                    Optional :class:`~arcgis.gis.Item` object whose type is ``StoryMap``.

                                .. note::
                                    If not specified, an empty ``StoryMap`` object is created with some
                                    useful defaults.

        ==================     ====================================================================
        """
        if gis is None:
            gis = env.active_gis
            self._gis = gis
        else:
            self._gis = gis
        if item and isinstance(item, str):
            self._item = gis.content.get(item)
            self._itemid = self._item.itemid
            self._properties = self._item.get_data()
        elif item and isinstance(item, Item) and "StoryMap" in item.typeKeywords:
            self._item = item
            self._itemid = self._item.itemid
            self._properties = self._item.get_data()
        elif item and isinstance(item, Item) and "StoryMap" not in item.typeKeywords:
            raise ValueError("Item is not a Story Map")
        else:
            template = r"src\arcgis\apps\storymap\templates\draft.json"
            f = open(template, "rb")
            self._properties = json.load(f)

            title = "StoryMap %s" % uuid.uuid4().hex[:10]
            typeKeywords = ",".join(
                [
                    "arcgis-storymaps",
                    "StoryMap",
                    "Web Application",
                    "smstatusdraft",
                    "smversiondraft:20.35.0",
                    "smsdraftresourceid:draft_" + str(int(time.time())) + ".json",
                ]
            )
            item_properties = {
                "title": title,
                "text": json.dumps(self._properties),
                "typeKeywords": typeKeywords,
                "type": "StoryMap",
            }
            item = self._gis.content.add(item_properties=item_properties)
            self._item = item
            self._itemid = item.itemid
            self._add_resource(
                file=template,
                resource_name="draft.json",
            )
            f.close()

    # ----------------------------------------------------------------------
    def __str__(self):
        return json.dumps(self._properties)

    # ----------------------------------------------------------------------
    def __repr__(self):
        return self.__str__()

    # ----------------------------------------------------------------------
    def _refresh(self):
        if self._item:
            self._properties = json.loads(self._item.get_data())

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """This property returns the storymap's JSON"""
        return self._properties

    # ----------------------------------------------------------------------
    @property
    def node_order(self):
        """This propertry returns the storymap's node order"""
        root_id = self.properties["root"]
        children = self.properties["nodes"][root_id]["children"]
        return tuple(children)

    # ----------------------------------------------------------------------
    @property
    def navigation_items(self):
        """
        This property returns a list of the nodes that are linked in the navigation node.
        """
        for node, node_info in self.properties["nodes"].items():
            for key, val in node_info.items():
                if key == "type" and val == "navigation":
                    node_id = node
        try:
            return self.properties["nodes"][node_id]["links"]
        except:
            return None

    # ----------------------------------------------------------------------
    def list_nodes(self, type: Optional[str] = None):
        """
        Find the nodes for each type of item.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        type                Optional string. The type of nodes that user wants returned.
                            If none specified, list of all nodes returned.

                            Values: "image" | "video" | "audio" | "webpage" | "webmap" | "text" |
                                    "button" | "separator"
        ===============     ====================================================================

        :return: A tuple of nodes for each type.

        ..note:
            The nodes are not in the order they appear in the story.
            To see all ordered nodes use: ```node_order``` property.
        """

        if type is None:
            return self._properties["nodes"].keys()
        else:
            type = type.lower().strip()
            if type == "webpage":
                type = "embed"
            nodes = []
            for node, node_info in self.properties["nodes"].items():
                for key, val in node_info.items():
                    if key == "type" and val == type:
                        nodes.append(node)
            return tuple(nodes)

    # ----------------------------------------------------------------------
    def story_cover(
        self,
        title: Optional[str] = None,
        type: str = "full",
        summary: Optional[str] = None,
        by_line: Optional[str] = None,
    ):
        """
        All stories come with a story cover node. This method allows you to edit the story cover.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Optional string. The title of the StoryMap cover.
        ---------------     --------------------------------------------------------------------
        type                Optional string. The type of story cover to be used in the story.
                            By default, it is “full”

                            Values: “full” | “sidebyside“ | “minimal"
        ---------------     --------------------------------------------------------------------
        summary             Optional string. The description of the story.
        ---------------     --------------------------------------------------------------------
        by_line             Optional string. Crediting the author(s).
        ===============     ====================================================================

        :return: Dictionary representation of the story cover node.
        """
        story_cover_node = self.node_order[0]
        orig_data = self.properties["nodes"][story_cover_node]["data"]

        self.properties["nodes"][story_cover_node] = {
            "type": "storycover",
            "data": {
                "type": type,
                "title": orig_data["title"] if title is None else title,
                "summary": orig_data["summary"] if summary is None else summary,
                "byline": orig_data["byline"] if by_line is None else by_line,
                "titlePanelPosition": "start",
            },
        }

        return self.properties["nodes"][story_cover_node]

    # ----------------------------------------------------------------------
    def navigation(
        self, nodes: Optional[list] = [{}], position: int = 1, hidden: bool = False
    ):
        """
        Story navigation is a way for authors to add headings as
        links to allow readers to navigate between different sections
        of a story. The story navigation node takes h2 blocks as its only allowed children.
        You can only have 10 h2 child nodes as visible and act as links within a story.
        The h2 node’s text can only allow up to 30 characters.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        nodes               Required list of dictionaries. The node ids to navigate to.
                            Use ```navigation_list``` property to get the current list.

                            ..note:
                                If a current list exists, copy and add to this list. Pass in entire
                                list again as current list will be overwritten.

                            Example:
                            nodes = [{
                                "nodeId": "n-R9XpeZ",
                                "nodeID": "n-8wzjrC",
                                "nodeID": "n-lA9Qac"
                            }]
        ---------------     --------------------------------------------------------------------
        position            Optional Integer. The position of the navigation on the story map.
                            To have navigation be under story cover, default is set to 1.
        ---------------     --------------------------------------------------------------------
        hidden              Optional boolean. If True, the navigation is hidden. Default is False
        ===============     ====================================================================
        """

        # Create ids
        node_id = "n-" + uuid.uuid4().hex[0:6]
        # Check if navigation node already exists
        for node, node_info in self.properties.items():
            for key, val in node_info.items():
                if key == "type" and val == "navigation":
                    node_id = node

        self.properties["nodes"][node_id] = {
            "type": "navigation",
            "data": {"links": nodes},
            "config": {"isHidden": hidden},
        }

        self._add_child(node_id=node_id, position=position)

    # ----------------------------------------------------------------------
    def end_credits(self, content=None, attribution=None, hidden=False):
        """
        Credits node is the last node in a story map.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        content             Optional list of Strings.
                            See ```add_text``` parameter text to understand format.
        ---------------     --------------------------------------------------------------------
        hidden              Optional boolean. If True, the navigation is hidden. Default is False
        ===============     ====================================================================
        """

        # Must take each string in content and create a new text node that is paragraph or h4
        # Take node id and add that to children of credits.

    # ----------------------------------------------------------------------
    def save(
        self,
        title: Optional[str] = None,
        tags: Optional[list] = None,
        access: str = "private",
        publish: bool = False,
    ):
        """
        Saves an Journal StoryMap to the GIS


        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Optional string. The title of the StoryMap.
        ---------------     --------------------------------------------------------------------
        tags                Optional string. The tags of the StoryMap.
        ---------------     --------------------------------------------------------------------
        access              Optional string. The access of the StoryMap such as 'private' or 'public'
        ---------------     --------------------------------------------------------------------
        publish             Optional boolean. If True, the story is saved and also published.
                            Default is false so story is saved with unpublished changes.
        ===============     ====================================================================


        :return: Boolean indicating success or failure.

        """
        # Update Item Resources
        draft = "draft_" + str(int(time.time())) + ".json"
        self._add_resource(
            resource_name=draft,
            text=json.dumps(self._properties),
        )

        # Find type keywords to use
        if publish is True:
            typeKeywords = ",".join(
                [
                    "arcgis-storymaps",
                    "Story Map",
                    "Web Application",
                    "smstatuspublished",
                    "smversionpublished:20.35.0",
                    "smpublisheddate:" + str(int(time.time())),
                    "smversiondraft:20.35.0",
                    "smdraftresourceid:" + draft,
                ]
            )
        else:
            typeKeywords = ",".join(
                [
                    "arcgis-storymaps",
                    "Story Map",
                    "Web Application",
                    "smstatusunpublishedchanges",
                    "smversiondraft:20.35.0",
                    "smdraftresourceid:" + draft,
                    "smversionpublished:20.35.0",
                    "smpublisheddate:" + str(int(time.time())),
                ]
            )

        p = {"typeKeywords": typeKeywords, "text": json.dumps(self._properties)}
        if title:
            p["title"] = title
        if tags:
            p["tags"] = tags
        p["access"] = access

        res = self._item.update(item_properties=p)
        self._item = self._gis.content.get(self._itemid)

        if publish is True:
            return self._item.publish(publish_parameters=p)
        else:
            return res

    # ----------------------------------------------------------------------
    def duplicate(self, title: Optional[str] = None):
        """
        Duplicate the story.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Optional string. The title of the duplicated story.
        ===============     ====================================================================
        """
        item = self._gis.content.get(self._itemid)

        if item._portal.is_arcgisonline is False:
            # TODO: TEST THIS
            return self._gis.content.clone_items(items=[item])
        else:
            return item.copy_item(
                title="(Copy) " + self._item.title if title is None else title,
                include_resources=True,
                include_private=True,
            )

    # ----------------------------------------------------------------------
    def add(self, item=None, position: Optional[int] = None):
        """
        Add and item to the story map

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        item                Optional item of type: Image, Video, Audio, WebPage, WebMap, Button,
                            or Text. If none is provided, a separator is added.
        ---------------     --------------------------------------------------------------------
        position            Optional Integer. Indicates the position in which the item will be
                            added. To see all node positions use the ```children``` property.
        ===============     ====================================================================

        :return: The node-id for the added item as a String.
        """

        if isinstance(item, Image):
            node, resource = item._add_image()
            self._add_resource(item._path, item._resource_id)
        elif isinstance(item, Video):
            node, resource = item._add_video()
            self._add_resource(item._path, item._resource_id)
        elif isinstance(item, Audio):
            node, resource = item._add_audio()
            self._add_resource(item._path, item._resource_id)
        elif isinstance(item, WebPage):
            node, resource = item._add_webpage()
        elif isinstance(item, WebMap):
            node, resource = item._add_webmap()
        elif isinstance(item, Button):
            node, resource = item._add_button()
        elif isinstance(item, Text):
            node, resource = item._add_text()
        else:
            node = {"type": "separator"}
            resource = None

        # Add to the nodes
        node_id = item._node if item is not None else uuid.uuid4().hex[0:6]
        self.properties["nodes"][node_id] = node

        # If resource was returned, add to resource nodes dictionary and story item
        if resource is not None:
            self.properties["resources"][item._resource_node] = resource
            # self._add_resource(item._path, item._resource_id)

        # Add to story children
        self._add_child(node_id=node_id, position=position)
        return node_id

    # ----------------------------------------------------------------------
    def move_node(
        self, node_id: str, position: Optional[int] = None, delete_current: bool = False
    ):
        """
        Move a node to another position. The node currently at that position will
        be moved down one space. The node at the current position can be deleted
        instead of moved if delete_current is set to True.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        node_id             Required String. The node id for the item that will be moved. Find a
                            list of node order by using the ```node_order``` property.
        ---------------     --------------------------------------------------------------------
        position            Optional Integer. Indicates the position in which the item will be
                            added. If no position is provided, the node will be placed at the end.
        ---------------     --------------------------------------------------------------------
        delete_current      Optional Boolean. If set to True, the node at the current position will
                            be deleted instead of moved down one space. Default is False.
        ===============     ====================================================================
        """
        root_id = self.properties["root"]
        children = self.properties["nodes"][root_id]["children"]

        # Remove node id from list since it will be added again at another position
        children.remove(node_id)

        if delete_current:
            if position == 0 or position == len(children):
                raise Exception(
                    "First and last nodes are reserved for Story Cover and Credits"
                )
            children.pop(position)

        self._add_child(node_id, position)

    # ----------------------------------------------------------------------
    def delete_node(self, node_id: str):
        """
        Delete a node from the story.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        node_id             Required String. The node id for the item that will be deleted.
                            To see the node ids for different types of items use ```list_nodes```
                            method.
        ===============     ====================================================================
        """
        root_id = self.properties["root"]
        children = self.properties["nodes"][root_id]["children"]

        # Remove from children of story
        children.remove(node_id)
        # Remove from nodes dictionary
        del self.properties["nodes"][node_id]
        # Remove from resources dictionary
        # Note: not all keys are in resources
        self.properties["nodes"].pop(node_id, None)

        return self.node_order

    # ----------------------------------------------------------------------
    def delete_story(self):
        """
        Deletes the story item.
        """
        item = self._gis.content.get(self._itemid)
        item.delete()

    # ----------------------------------------------------------------------
    def _add_child(self, node_id, position=None):
        """
        A story node has children. Children is a list of item nodes that are in
        the story. The order of the list determines the order that the nodes
        appear in the story.

        A user can change the position of the items however the first and last
        nodes are reserved for story_cover and credits, respectively.
        """
        # Add to story children, position counts
        # Last node is always credits and first node is always story cover
        root_id = self.properties["root"]
        last = len(self.properties["nodes"][root_id]["children"]) - 1

        if position and position < last and position != 0:
            self.properties["nodes"][root_id]["children"].insert(position, node_id)
        elif position and position == 0:
            self.properties["nodes"][root_id]["children"].insert(1, node_id)
        else:
            # last node is always credits
            self.properties["nodes"][root_id]["children"].insert(last, node_id)

    # ----------------------------------------------------------------------
    def _add_resource(self, file=None, resource_name=None, text=None):
        """
        The add resources operation (POST only) allows to add new file resources
        to an existing item, for example, an image that is used as custom logo
        for Report Template. All the files are added to resources folder of the item.
        File resources use storage space from your quota and are scanned for viruses.
        The item size is updated to include the size of added resource files.
        There is a limit of 1000 files per item (except Style items). A maximum
        of 50 files can be added each request. Each file should be no more than 50 Mb.
        The maximum size of all of the file resources for an item is 10 GB.
        """
        # first need to do an addResources call for the draft
        url = (
            "content/users/"
            + self._gis._username
            + "/items/"
            + self._item.itemid
            + "/addResources"
        )
        files = []
        if file and os.path.isfile(os.path.abspath(file)):
            files.append(("file", file, os.path.basename(file)))
        elif file and os.path.isfile(os.path.abspath(file)) == False:
            raise RuntimeError("File(" + file + ") not found.")

        params = {"f": "json", "fileName": resource_name, "access": self._item.access}

        if text is not None:
            params["text"] = text

        resp = self._gis._portal.con.post(url, params, files=files, compress=False)
        self._item = self._gis.content.get(self._itemid)
        return resp


###############################################################################################################
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
            "config": {
                "size": self._display,
            },
        }

        # Create resource node
        resource = {
            "type": "video",
            "data": {
                "resourceId": self._resource_id,
                "provider": "item-resource",
            },
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
            "config": {
                "size": self._display,
            },
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
            "data": {
                "type": self._style,
                "text": self._text,
                "customTextColors": self._color,
            },
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
class WebMap(object):
    """
    Class representing a webmap for the story

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

        self._resource_id = str(int(time.time())) + "_WebMap"

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
                "itemType": "Web Map",
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
