from typing import Optional, Union
import uuid
from enum import Enum
from arcgis.apps.storymap.story_content import Image
from arcgis.auth.tools import LazyLoader

arcgis = LazyLoader("arcgis")
Content = LazyLoader("arcgis.apps.storymap.story_content")
json = LazyLoader("json")
time = LazyLoader("time")


class Themes(Enum):
    """
    Represents the Supported Theme Type Enumerations.
    Example: story_map.theme(Theme.Slate)
    """

    SUMMIT = "summit"
    OBSIDIAN = "obsidian"
    RIDGELINE = "ridgeline"
    MESA = "mesa"
    TIDAL = "tidal"
    SLATE = "slate"


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

    def __init__(self, item=None, gis=None):
        if gis is None:
            gis = arcgis.env.active_gis
            self._gis = gis
        else:
            self._gis = gis
        if gis._portal.is_logged_in is False:
            # CHECK TO SEE IF AUTHENTICATED
            raise Exception("Must be logged into an Enterprise Account")
        if item and isinstance(item, str):
            item = gis.content.get(item)
        if item and isinstance(item, arcgis.gis.Item) and item.type == "StoryMap":
            self._item = item
            self._itemid = self._item.itemid
            self._properties = self._item.get_data()
            self._resources = self._item.resources.list()
            # If story is a draft, get properties from resource file.
            if (
                self._properties == {}
                or "unpublished" in self._properties
                and self._properties["unpublished"] is True
            ):
                for resource in self._resources:
                    for key, val in resource.items():
                        if key == "resource" and val == "draft.json":
                            # Open JSON file for properties
                            data = self._item.resources.get(val, try_json=True)
                            self._properties = data
        elif (
            item
            and isinstance(item, arcgis.gis.Item)
            and "StoryMap" not in item.typeKeywords
        ):
            raise ValueError("Item is not a Story Map")
        else:
            self._create_new_storymap()

    # ----------------------------------------------------------------------
    def _create_new_storymap(self):
        template = arcgis.apps.storymap._ref.storymap_2
        self._properties = template
        text = json.dumps(template)
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
        self._add_resource(resource_name="draft.json", text=text)
        self._resources = self._item.resources.list()

    # ----------------------------------------------------------------------
    def _repr_html_(self):
        """
        HTML Representation for IPython Notebook
        """
        try:
            return (
                "<iframe src="
                + self._item.url
                + "title="
                + self._item.title
                + "></iframe>"
            )
        except:
            return None

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
        root_id = self._properties["root"]
        children = self._properties["nodes"][root_id]["children"]
        nodes = self._properties["nodes"]

        node_order = []
        for child in children:
            if child in nodes:
                node = self._assign_node_class(child)
                node_order.append({child: node})
        return node_order

    # ----------------------------------------------------------------------
    @property
    def navigation(self):
        """
        Get a list of the nodes that are linked in the navigation node.
        """
        nav = self.list("navigation")[0]
        for key, value in nav.items():
            node_id = key
        try:
            return self._properties["nodes"][node_id]["data"]["links"]
        except:
            return None

    # ----------------------------------------------------------------------
    def list(self, type: Optional[str] = None, node_id: Optional[str] = None):
        """
        Find the nodes for each type of item.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        type                Optional string. The type of nodes that user wants returned.
                            If none specified, list of all nodes returned.

                            Values: "image" | "video" | "audio" | "embed" | "webmap" | "text" |
                                    "button" | "separator" | "expressmap" | "webscene" | "immersive"
        ---------------     --------------------------------------------------------------------
        node_id             Optional string. The node id for the node that should be returned.
        ===============     ====================================================================

        :return: List of node ids and their types in order of appearance in the story map.

        ..code-block:: python

            >>> story = StoryMap(<story item>)
            >>> story.list_nodes("text")

        """
        spec_type = []

        if type is None and node_id is None:
            return self.node_order
        elif node_id is not None:
            # return a specific node
            all_nodes = self.node_order
            for node in all_nodes:
                id = list(node.keys())[0]
                if node_id == id:
                    return node
        else:
            # return all nodes of a certain type
            all_nodes = self.node_order
            for node in all_nodes:
                keyword = list(node.values())[0]
                if isinstance(keyword, str):
                    # Not a type of story content
                    if type.lower() in keyword:
                        spec_type.append(node)
                else:
                    # Find all story content instances
                    if type.lower() in keyword._type:
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
        credits = self._properties["nodes"][credits_node]

        # Create new content node
        content_node = "n-" + uuid.uuid4().hex[0:6]
        self._properties["nodes"][content_node] = {
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
        image: Optional[Image] = None,
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
        ---------------     --------------------------------------------------------------------
        image               Optional Image object. The cover image for the story cover.
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
        orig_data = self._properties["nodes"][story_cover_node]["data"]

        self._properties["nodes"][story_cover_node] = {
            "type": "storycover",
            "data": {
                "type": type,
                "title": orig_data["title"] if title is None else title,
                "summary": orig_data["summary"] if summary is None else summary,
                "byline": orig_data["byline"] if by_line is None else by_line,
                "titlePanelPosition": "start",
            },
        }
        if image is not None:
            self._properties["nodes"][story_cover_node]["children"] = [image._node]
        return self._properties["nodes"][story_cover_node]

    # ----------------------------------------------------------------------
    def navigation(self, nodes: Optional[list] = None, hidden: Optional[bool] = None):
        """
        Story navigation is a way for authors to add headings as
        links to allow readers to navigate between different sections
        of a story. The story navigation node takes h2 blocks as its only allowed children.
        You can only have 10 h2 child nodes as visible and act as links within a story.
        The h2 node’s text can only allow up to 30 characters.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        nodes               Optional list of dictionaries. The node ids to navigate to.
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
        hidden              Optional boolean. If True, the navigation is hidden.
        ===============     ====================================================================
        """

        # Check if navigation node already exists
        for node, node_info in self._properties["nodes"].items():
            for key, val in node_info.items():
                if key == "type" and val == "navigation":
                    node_id = node

        # If none is provided, set to what is already there
        if nodes is None:
            nodes = self._properties["nodes"][node_id]["data"]["links"]
        if hidden is None:
            hidden = self._properties["nodes"][node_id]["config"]["isHidden"]

        # Update navigation
        self._properties["nodes"][node_id] = {
            "type": "navigation",
            "data": {"links": nodes},
            "config": {"isHidden": hidden},
        }

        return self._properties["nodes"][node_id]

    # ----------------------------------------------------------------------
    def theme(self, theme: Themes = Themes.SUMMIT):
        """
        Each story has a theme node in it's resources. This method can be used to change the theme

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        theme               Required Themes Style. The theme to set the story to.

                            Values: SUMMIT | TIDAL | MESA | RIDGELINE | SLATE | OBSIDIAN
        ===============     ====================================================================
        """

        for node, node_info in self._properties["resources"].items():
            for key, val in node_info.items():
                if key == "type" and val == "story-theme":
                    if isinstance(theme, Themes):
                        self._properties["resources"][node]["data"][
                            "themeId"
                        ] = theme.value

    # ----------------------------------------------------------------------
    def add(
        self,
        content: Optional[
            Union[
                Content.Image,
                Content.Video,
                Content.Audio,
                Content.Embed,
                Content.Map,
                Content.Button,
                Content.Text,
            ]
        ] = None,
        caption: Optional[str] = None,
        alt_text: Optional[str] = None,
        display: str = None,
        position: Optional[int] = None,
    ):
        """
        Add and content to the story map

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        content             Optional content of type: Image, Video, Audio, Embed, Map, Button,
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
        position            Optional Integer. Indicates the position in which the content will be
                            added. To see all node positions use the ```children``` property.
        ===============     ====================================================================

        :return: The node-id for the added content as a String.

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
        if content and content._node in self._properties["nodes"]:
            raise Exception("This node already exists. Please try updating instead.")

        node_id = content._node if content is not None else uuid.uuid4().hex[0:6]

        if isinstance(content, Content.Image):
            content._add_image(caption, alt_text, display, self)
        elif isinstance(content, Content.Video):
            content._add_video(caption, alt_text, display, self)
        elif isinstance(content, Content.Audio):
            content._add_audio(caption, alt_text, display, self)
        elif isinstance(content, Content.Map):
            content._add_map(caption, alt_text, display, story=self)
        elif isinstance(content, Content.Embed):
            content._add_link(caption, alt_text, self)
        elif isinstance(content, Content.Button):
            content._add_button(self)
        elif isinstance(content, Content.Text):
            content._add_text(self)
        else:
            self._properties["nodes"][node_id] = {"type": "separator"}

        # Add to story children
        self._add_child(node_id=node_id, position=position)
        return node_id

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
        node_id             Required String. The node id for the content that will be moved. Find a
                            list of node order by using the ```node_order``` property.
        ---------------     --------------------------------------------------------------------
        position            Optional Integer. Indicates the position in which the content will be
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
        root_id = self._properties["root"]
        children = self._properties["nodes"][root_id]["children"]

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

        return res

    # ----------------------------------------------------------------------
    def delete_story(self):
        """
        Deletes the story item.
        """
        # Check if item id exists
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
    def _delete(self, node_id, resource_id=None):
        """
        Delete a node from the story.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        node_id             Required String. The node id for the content that will be deleted.
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
        for key, value in self._properties["nodes"].items():
            if key == node_id:
                root_id = self._properties["root"]
                children = self._properties["nodes"][root_id]["children"]

                # Remove from children of story
                if node_id in children:
                    children.remove(node_id)

                # Remove from nodes dictionary
                del self._properties["nodes"][node_id]

                # Remove from resources dictionary
                # Note: not all keys are in resources
                resource = self._properties["resources"].pop(resource_id, None)

                if resource is not None:
                    self._remove_resource(resource["data"]["resourceId"])
                return True
            else:
                return False

    # ----------------------------------------------------------------------
    def _add_child(self, node_id, position=None):
        """
        A story node has children. Children is a list of item nodes that are in
        the story. The order of the list determines the order that the nodes
        appear in the story. First and last nodes are reserved for story_cover
        and credits. The second node is always navigation. If visible is not set
        to True is simply won't be seen but stays in position 2.
        """
        root_id = self._properties["root"]
        last = len(self._properties["nodes"][root_id]["children"]) - 1

        if position and position < last and position != 0:
            self._properties["nodes"][root_id]["children"].insert(position, node_id)
        elif position and (position == 0 or position == 1):
            self._properties["nodes"][root_id]["children"].insert(2, node_id)
        else:
            self._properties["nodes"][root_id]["children"].insert(last, node_id)

    # ----------------------------------------------------------------------
    def _add_resource(self, file=None, resource_name=None, text=None):
        """
        See :class:`~arcgis.gis.ResourceManager`
        """
        resource_manager = arcgis.gis.ResourceManager(self._item, self._gis)
        is_present = False
        if file:
            for resource in self._resources:
                if resource["resource"] in file:
                    is_present = True
                    resp = True
        if is_present is False:
            resp = resource_manager.add(file=file, file_name=resource_name, text=text)
        self._resources = self._item.resources.list()
        return resp

    # ----------------------------------------------------------------------
    def _remove_resource(self, file=None):
        """
        See :class:`~arcgis.gis.ResourceManager`
        """
        resource_manager = arcgis.gis.ResourceManager(self._item, self._gis)
        resp = resource_manager.remove(file=file)
        self._resources = self._item.resources.list()
        return resp

    # ----------------------------------------------------------------------
    def _assign_node_class(self, node_id):
        node_type = self._properties["nodes"][node_id]["type"]
        if node_type == "image":
            node = Content.Image(story=self, node_id=node_id)
        elif node_type == "video":
            node = Content.Video(story=self, node_id=node_id)
        elif node_type == "audio":
            node = Content.Audio(story=self, node_id=node_id)
        elif node_type == "embed":
            # embed has subtype: video, audio, or link
            subtype = self._properties["nodes"][node_id]["data"]["embedType"]
            if subtype == "video":
                node = Content.Video(story=self, node_id=node_id)
            elif subtype == "audio":
                node = Content.Audio(story=self, node_id=node_id)
            else:
                node = Content.Embed(story=self, node_id=node_id)
        elif node_type == "webmap":
            node = Content.Map(story=self, node_id=node_id)
        elif node_type == "text":
            node = Content.Text(story=self, node_id=node_id)
        elif node_type == "button":
            node = Content.Button(story=self, node_id=node_id)
        elif node_type == "swipe":
            node = Content.Swipe(node_id, self)
        elif node_type == "immersive":
            # immersive has subtype sidecar, and tour
            subtype = self._properties["nodes"][node_id]["data"]["type"]
            if subtype == "sidecar":
                node = Content.Sidecar(node_id, self)
            else:
                node = subtype
        else:
            node = node_type
        return node
