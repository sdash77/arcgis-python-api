import os
import time
import json
import mimetypes
from typing import Optional, Union
from arcgis import env
from arcgis.gis import GIS, Item
import uuid
from arcgis.apps.storymap import (
    Text,
    Image,
    Video,
    WebPage,
    Audio,
    Button,
    Map,
)


class StoryMap(object):
    """ """

    _properties = None
    _gis = None
    _itemid = None
    _item = None
    _resources = None

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
            self._resources = self._item.resources.list()
        elif item and isinstance(item, Item) and "StoryMap" in item.typeKeywords:
            self._item = item
            self._itemid = self._item.itemid
            self._properties = self._item.get_data()
            self._resources = self._item.resources.list()
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
                file=template, resource_name="draft.json",
            )
            self._resources = self._item.resources.list()
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
        nodes = self.properties["nodes"]

        node_order = []
        for child in children:
            if child in nodes:
                node_type = self.properties["nodes"][child]["type"]
                if node_type == "text":
                    subtype = self.properties["nodes"][child]["data"]["type"]
                    node_order.append({child: node_type + ", " + subtype})
                else:
                    node_order.append({child: node_type})
        return tuple(node_order)

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
                                    "button" | "separator" | "expressmap" | "webscene" | "immersive" |
        ===============     ====================================================================

        :return: A tuple of nodes for each type.

        ..note:
            The nodes are not in the order they appear in the story.
            To see all ordered nodes use: ```node_order``` property.
        """

        if type is None:
            return self.node_order
        else:
            all_nodes = self.node_order
            spec_type = []
            for node in all_nodes:
                if type in node.values():
                    spec_type.append(node)
            return spec_type

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
            resource_name=draft, text=json.dumps(self._properties),
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
        elif isinstance(item, Map):
            node, resource = item._add_webmap()
            self._add_resource(
                resource_name=item._resource_id, text=json.dumps(item._path)
            )
        elif isinstance(item, WebPage):
            node, resource = item._add_webpage()
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

        # Add to story children
        self._add_child(node_id=node_id, position=position)
        return node_id

    # ----------------------------------------------------------------------
    def update(
        self,
        node_id: str,
        path: Optional[Union[str, Item]] = None,
        caption: Optional[str] = None,
        alt_text: Optional[str] = None,
        display: Optional[str] = None,
        button_text: Optional[str] = None,
        button_link: Optional[str] = None,
    ):
        """
        Update an existing node of type Image, Video, WebPage, or Audio.
        Can also be used to update the text or link of a button.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        node_id             Required String. The node id for the item that will be updated. Find a
                            list of node order by using the ```node_order``` property.
        ---------------     --------------------------------------------------------------------
        path                Optional String or Item of type WebMap or WebScene. The path or item
                            that will replace the current item.
        ---------------     --------------------------------------------------------------------
        caption             Optional String. New caption to insert.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional String. New alt_text to insert.
        ---------------     --------------------------------------------------------------------
        display             Optional String. New display style to insert.
        ---------------     --------------------------------------------------------------------
        button_text         Optional String. To update the text on a Button.
        ---------------     --------------------------------------------------------------------
        button_link         Optional String. To update the link on a Button.
        ===============     ====================================================================

        :return:
        """
        if isinstance(path, Item):
            if path.type != "Web Map" or path.type != "Web Scene":
                raise Exception("New item must be of type Web Map or Web Scene")
        elif isinstance(path, str):
            mt = mimetypes.guess_type(path)[0].lower()
            if "image" in mt:
                new_item = Image(path)
                new_item._update_image(node_id, self)
            elif "video" in mt:
                new_item = Video(path, caption, alt_text, display)
                new_item._update_video(node_id, self)
            elif "audio" in mt:
                new_item = Audio(path, caption, alt_text, display)
                new_item._update_audio(node_id, self)
            else:
                new_item = WebPage(path, caption, alt_text, display)
                new_item._update_webpage(node_id, self)
        elif path is None:
            return self._update_properties(
                node_id, caption, alt_text, display, button_text, button_link
            )

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


        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        file              Required string. The path to the file on disk to be used for
                          overwriting an existing file resource.
        ----------------  ---------------------------------------------------------------
        file_name         Optional string. The destination name for the file used to add
                          an existing resource, or to be used together with the text parameter
                          as file name for it.
        ----------------  ---------------------------------------------------------------
        text              Optional string. Text input to be added as a file resource,
                          used together with file_name.
        ================  ===============================================================
        """
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
        self._resources = self._item.resources.list()
        return resp

    # ----------------------------------------------------------------------
    def _update_resource(self, file=None, resource_name=None, text=None):
        """
        The ``update`` operation allows you to update existing file resources of an item.
        File resources use storage space from your quota and are scanned for viruses. The item size
        is updated to include the size of updated resource files.

        Supported file formats are: JSON, XML, TXT, PNG, JPEG, GIF, BMP, PDF, and ZIP.
        This operation is only available to the item owner and the organization administrator.

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        file              Required string. The path to the file on disk to be used for
                          overwriting an existing file resource.
        ----------------  ---------------------------------------------------------------
        file_name         Optional string. The destination name for the file used to update
                          an existing resource, or to be used together with the text parameter
                          as file name for it.

                          For example, you can use fileName=banner.png to update an existing
                          resource banner.png with a file called billboard.png without
                          renaming the file locally.
        ----------------  ---------------------------------------------------------------
        text              Optional string. Text input to be added as a file resource,
                          used together with file_name.
        ================  ===============================================================
        """

        url = (
            "content/users/"
            + self.gis._username
            + "/items/"
            + self._item.itemid
            + "/updateResources"
        )

        files = []  # create a list of named tuples to hold list of files
        if not os.path.isfile(os.path.abspath(file)):
            raise RuntimeError("File(" + file + ") not found.")
        files.append(("file", file, os.path.basename(file)))

        params = {}
        params["f"] = "json"

        if resource_name is not None:
            params["fileName"] = resource_name
        if text is not None:
            params["text"] = text

        resp = self._portal.con.post(url, params, files=files)
        return resp

    # ----------------------------------------------------------------------
    def _update_properties(
        self, node_id, caption, alt_text, display, button_text, button_link
    ):
        node_type = self.properties["nodes"][node_id]["type"]

        # Update main node
        if caption is not None:
            self.properties["nodes"][node_id]["data"]["caption"] = caption
        if alt_text is not None:
            self.properties["nodes"][node_id]["data"]["alt"] = alt_text
        if display is not None and node_type in ["image", "video", "audio", "webmap"]:
            self.properties["nodes"][node_id]["config"]["size"] = display
        if node_type == "button":
            if button_text is not None:
                self.properties["nodes"][node_id]["data"]["text"] = button_text
            if button_link is not None:
                self.properties["nodes"][node_id]["data"]["link"] = button_link

        return self.properties["nodes"][node_id]


###############################################################################################################

