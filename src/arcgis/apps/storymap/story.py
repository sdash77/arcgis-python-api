import time
import json
import mimetypes
from typing import Optional, Union
from arcgis import env
from arcgis.gis import GIS, Item, ResourceManager
import uuid
from arcgis.apps.storymap.story_content import (
    Text,
    Image,
    Video,
    WebPage,
    Audio,
    Button,
    Map,
)

###############################################################################################################
class StoryMap(object):
    """
    A Story Map is a web map that has been thoughtfully created, given context, and provided
    with supporting information so it becomes a stand-alone resource. It integrates maps, legends,
    text, photos, and video and provides functionality, such as swipe, pop-ups, and time sliders,
    that helps users explore this content.

    ArcGIS StoryMaps is the next-generation storytelling tool in ArcGIS, and story authors are
    encouraged to use this tool to create stories.
    """

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
            item = gis.content.get(item)
        if item and isinstance(item, Item) and "StoryMap" in item.typeKeywords:
            self._item = item
            self._itemid = self._item.itemid
            self._properties = self._item.get_data()
            self._resources = self._item.resources.list()
            if (
                "unpublished" in self.properties
                and self.properties["unpublished"] is True
            ):
                raise ValueError("StoryMap cannot be draft")
        elif item and isinstance(item, Item) and "StoryMap" not in item.typeKeywords:
            raise ValueError("Item is not a Story Map")
        else:
            self._create_new_webmap()

    # ----------------------------------------------------------------------
    def _create_new_webmap(self):
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
            self,
            file=template,
            resource_name="draft.json",
        )
        self._resources = self._item.resources.list()
        f.close()

    # ----------------------------------------------------------------------
    def _repr_html_(self):
        """
        HTML Representation for IPython Notebook
        """
        return 'GIS @ <a href="' + self.url + '">' + self.url + "</a>"

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
        """
        This propertry returns the storymap's main nodes in order of appearance in the story

        To see sub-nodes then use the corresponding immersive class to list the nodes for
        immersive types.
        """
        root_id = self.properties["root"]
        children = self.properties["nodes"][root_id]["children"]
        nodes = self.properties["nodes"]

        node_order = []
        for child in children:
            if child in nodes:
                node_type = self.properties["nodes"][child]["type"]
                if node_type == "text" or node_type == "immersive":
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
                                    "button" | "separator" | "expressmap" | "webscene" | "immersive"|
                                    "swipe"
        ===============     ====================================================================

        :return: List of node ids and their types in order of appearance in the story map.

        ..code-block:: python

            >>> story = StoryMap(<story item>)
            >>> story.list_nodes("text")

        """
        spec_type = []

        if type is None:
            return self.node_order
        else:
            all_nodes = self.node_order
            for node in all_nodes:
                keywords = list(node.values())[0].split(",")
                if type.lower() in keywords:
                    spec_type.append(node)
            return tuple(spec_type)

    # ----------------------------------------------------------------------
    def credits(
        self,
        content: Optional[str] = None,
        attribution: Optional[str] = None,
    ):
        """
        Add credits to the story.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        content             Optional String. The content to be added. (Seen on the left side of
                            the credits.)

                            Make sure text has '<strong> </strong>' tags.
        ---------------     --------------------------------------------------------------------
        attribution         Optional String. The attribution to be added. (Seen on right side of
                            the credits.)
        ===============     ====================================================================
        """
        # Find credit node
        dict_node = self.list_nodes("credits")[0]
        for key, value in dict_node.items():
            credits_node = key
        credits = self.properties["nodes"][credits_node]

        # Create new content node
        content_node = "n-" + uuid.uuid4().hex[0:6]
        self.properties["nodes"][content_node] = {
            "type": "attribution",
            "data": {"content": content, "attribution": attribution},
        }

        # Add to children of credits
        credits["children"].append(content_node)
        return credits["children"]

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

        ..code-block:: python

            story = StoryMap(<story item>)
            story.story_cover(title="My Story Title", type="minimal", summary="My little summary", by_line="python_dev")
            story.save()

        """
        dict_node = self.node_order[0]
        for key, value in dict_node.items():
            story_cover_node = key
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
    def navigation(self, nodes: list, position: int = 1, hidden: bool = False):
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
        for node, node_info in self.properties["nodes"].items():
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
    def theme(self, theme: str = "summit"):
        """
        Each story has a theme node in it's resources. This method can be used to change the theme

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        theme               Required String. The theme to set the story to.

                            Values: "summit" | "obsidian" | "ridgeline" | "mesa" | "tidal" |
                                    "slate"
        ===============     ====================================================================
        """

        for node, node_info in self.properties["resources"].items():
            for key, val in node_info.items():
                if key == "type" and val == "story-theme":
                    node_info["data"]["themeId"] = theme

    # ----------------------------------------------------------------------
    def save(
        self,
        title: Optional[str] = None,
        tags: Optional[list] = None,
        access: str = "private",
        publish: bool = False,
    ):
        """
        Saves an StoryMap to the GIS

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
        # Remove old draft item
        for resource in self._resources:
            if "draft_" in resource["resource"]:
                self._remove_resource(file=resource["resource"])

        # Add new draft
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
    def add(
        self,
        item=None,
        caption: Optional[str] = None,
        alt_text: Optional[str] = None,
        display: str = "float",
        position: Optional[int] = None,
    ):
        """
        Add and item to the story map

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        item                Optional item of type: Image, Video, Audio, WebPage, WebMap, Button,
                            or Text. If none is provided, a separator is added.
        ---------------     --------------------------------------------------------------------
        caption             Optional String. Custom text to caption the webmap.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional String. Custom text to be used for screen readers.
        ---------------     --------------------------------------------------------------------
        display             Optional String. How the item will be displayed in the story map.
                            Used for Image, Video, Audio, or Map object.

                            Values: "small" | "wide" | "full" | "float"
        ---------------     --------------------------------------------------------------------
        position            Optional Integer. Indicates the position in which the item will be
                            added. To see all node positions use the ```children``` property.
        ===============     ====================================================================

        :return: The node-id for the added item as a String.

        .. code-block:: python

            new_story = StoryMap()

            # Example with Image
            >>> image1 = Image("<image-path>.jpg/jpeg/png/gif ")
            >>> new_node = new_story.add(image1, "my caption", "my alt-text", "float", 2)

            # Example with Map
            >>> my_map = Map(<item-id of type webmap>)
            >>> new_node = new_story.add(my_map, "A map caption", "A new map alt-text", "wide")

            # Example to add a Separator
            >>> new_node = new_story.add()

            >>> print(new_story.node_order)

        """
        if item and item._node in self.properties["nodes"]:
            raise Exception("This node already exists. Please try updating instead.")

        node_id = item._node if item is not None else uuid.uuid4().hex[0:6]

        if isinstance(item, Image):
            item._add_image(self, caption, alt_text, display)
        elif isinstance(item, Video):
            item._add_video(self, caption, alt_text, display)
        elif isinstance(item, Audio):
            item._add_audio(self, caption, alt_text, display)
        elif isinstance(item, Map):
            item._add_webmap(self, caption, alt_text, display)
        elif isinstance(item, WebPage):
            item._add_webpage(self, caption, alt_text)
        elif isinstance(item, Button):
            item._add_button(self)
        elif isinstance(item, Text):
            item._add_text(self)
        else:
            self.properties["nodes"][node_id] = {"type": "separator"}

        # Add to story children
        self._add_child(node_id=node_id, position=position)
        return node_id

    # ----------------------------------------------------------------------
    def update(
        self,
        node_id: str,
        item: Optional[Union[str, Item, Map, Image, Video, WebPage, Audio]] = None,
        caption: Optional[str] = None,
        alt_text: Optional[str] = None,
        display: Optional[str] = None,
        button_text: Optional[str] = None,
        button_link: Optional[str] = None,
        text: Optional[str] = None,
        text_style: Optional[str] = None,
    ):
        """
        Update Story Items in various ways:

        - Update item path for Map, Image, Video, WebPage, or Audio node
        - Update caption and alt_text for all node types
        - Update button link and/or text for a Button node
        - Update text or text style for a Text node

        ..note:
            To update immersive node use the Swipe, Sidecar, or Slideshow class.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        node_id             Required String. The node id for the item that will be updated. Find a
                            list of node order by using the ```node_order``` property.
        ---------------     --------------------------------------------------------------------
        item                Optional String or Story Map Content Item.
                            Values:
                            - Story Map Item of type: 'Image', 'Video', 'Audio', 'Webpage', or 'Map'.
                            - Item: :class:`~arcgis.gis.Item` of type 'WebMap' or 'WebScene'
                            - String: The url or file path for the new item.
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
        ---------------     --------------------------------------------------------------------
        text                Optional String. To update the text of a Text node.
        ---------------     --------------------------------------------------------------------
        text_style          Optional String. To update the text style of a Text node.
        ===============     ====================================================================

        .. code-block:: python

            new_story = StoryMap()

            # Example with Image
            >>> image1 = Image("<image-path>.jpg/jpeg/png/gif")
            >>> image2 = Image("<image-path>.jpg/jpeg/png/gif")
            >>> new_node = new_story.add(image1, "my caption", "my alt-text", "float", 2)
            >>> new_story.update(new_node, image2, "new caption")

            # Example with Map
            >>> my_map = Map(<item-id of type webmap>)
            >>> new_node = new_story.add(my_map, "A map caption", "A new map alt-text", "wide")
            >>> new_story.update(new_node, <Item of type webmap>)

            # Example to add a Separator
            >>> new_node = new_story.add()

            >>> print(new_story.node_order)

        """
        # Update path if new path given
        if isinstance(item, Item) or isinstance(item, Map):
            if item.type != "Web Map" or item.type != "Web Scene":
                raise Exception("New item must be of type Web Map or Web Scene")
            if isinstance(item, Item):
                item = Map(item)
            item._update_map(node_id, self)
        elif isinstance(item, str):
            mt = mimetypes.guess_type(item)[0].lower()
            if "image" in mt:
                item = Image(item)
            elif "video" in mt:
                item = Video(item)
            elif "audio" in mt:
                item = Audio(item)
            else:
                item = WebPage(item)
        # Update item
        if isinstance(item, Image):
            item._update_image(node_id, self)
        elif isinstance(item, Video):
            item._update_video(node_id, self)
        elif isinstance(item, WebPage):
            item._update_webpage(node_id, self)
        elif isinstance(item, Audio):
            item._update_audio(node_id, self)

        # Update properties if new properties given
        if caption or alt_text or display:
            self._update_properties(node_id, caption, alt_text, display)
        if button_text or button_link:
            new_button = Button(link=button_link, text=button_text)
            new_button._update_button(node_id, self)
        if text or text_style:
            new_text = Text(text=text, style=text_style)
            new_text._update_text(node_id, self)

    # ----------------------------------------------------------------------
    def move(
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

        .. code-block:: python

            new_story = StoryMap()

            # Example with Image
            >>> image1 = Image("<image-path>.jpg/jpeg/png/gif")
            >>> image2 = Image("<image-path>.jpg/jpeg/png/gif")
            >>> new_node = new_story.add(image1, "my caption", "my alt-text", "float", 2)
            >>> new_story.add(image2)
            >>> new_story.move(new_node, 3, False)

        """
        root_id = self.properties["root"]
        children = self.properties["nodes"][root_id]["children"]

        # Remove node id from list since it will be added again at another position
        children.remove(node_id)

        # If delete_current is True then remove the node currently at this position
        if delete_current:
            if position == 0 or position == len(children):
                raise Exception(
                    "First and last nodes are reserved for Story Cover and Credits"
                )
            children.pop(position)

        # Add node to new position
        self._add_child(node_id, position)

    # ----------------------------------------------------------------------
    def delete(self, node_id: str):
        """
        Delete a node from the story.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        node_id             Required String. The node id for the item that will be deleted.
                            To see the node ids for different types of items use ```list_nodes```
                            method.
        ===============     ====================================================================

        ..code-block:: python

            new_story = StoryMap()

            # Example with Image
            >>> image1 = Image("<image-path>.jpg/jpeg/png/gif")
            >>> new_node = new_story.add(image1, "my caption", "my alt-text", "float", 2)
            >>> new_story.delete(new_node)

        """
        root_id = self.properties["root"]
        children = self.properties["nodes"][root_id]["children"]

        # Remove from children of story
        if node_id in children:
            children.remove(node_id)

        # Remove from nodes dictionary
        del self.properties["nodes"][node_id]

        # Remove from resources dictionary
        # Note: not all keys are in resources
        resource = self.properties["resources"].pop(node_id, None)

        if resource is not None:
            self._remove_resource(resource["data"]["resourceId"])

    # ----------------------------------------------------------------------
    def delete_story(self):
        """
        Deletes the story item.
        """
        item = self._gis.content.get(self._itemid)
        item.delete()

    # ----------------------------------------------------------------------
    def duplicate_story(self, title: Optional[str] = None):
        """
        Duplicate the story.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Optional string. The title of the duplicated story.
        ===============     ====================================================================

        ..code-block:: python

            story = StoryMap(<story item>)
            story.duplicate("A Story Copy")

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
    def _add_child(self, node_id, position=None):
        """
        A story node has children. Children is a list of item nodes that are in
        the story. The order of the list determines the order that the nodes
        appear in the story. First and last nodes are reserved for story_cover
        and credits.
        """
        root_id = self.properties["root"]
        last = len(self.properties["nodes"][root_id]["children"]) - 1

        if position and position < last and position != 0:
            self.properties["nodes"][root_id]["children"].insert(position, node_id)
        elif position and position == 0:
            self.properties["nodes"][root_id]["children"].insert(1, node_id)
        else:
            self.properties["nodes"][root_id]["children"].insert(last, node_id)

    # ----------------------------------------------------------------------
    def _add_resource(self, file=None, resource_name=None, text=None):
        """
        See :class:`~arcgis.gis.ResourceManager`
        """
        resource_manager = ResourceManager(self._item, self._gis)
        resp = resource_manager.add(file=file, file_name=resource_name, text=text)
        self._resources = self._item.resources.list()
        return resp

    # ----------------------------------------------------------------------
    def _remove_resource(self, file=None):
        """
        See :class:`~arcgis.gis.ResourceManager`
        """
        resource_manager = ResourceManager(self._item, self._gis)
        resp = resource_manager.remove(file=file)
        self._resources = self._item.resources.list()
        return resp

    # ----------------------------------------------------------------------
    def _update_properties(self, node_id, caption, alt_text, display):
        node_type = self.properties["nodes"][node_id]["type"]
        # Update main node
        if caption is not None:
            self.properties["nodes"][node_id]["data"]["caption"] = caption
        if alt_text is not None:
            self.properties["nodes"][node_id]["data"]["alt"] = alt_text
        if display is not None and node_type in ["image", "video", "audio", "webmap"]:
            self.properties["nodes"][node_id]["config"]["size"] = display
        return self.properties["nodes"][node_id]
