from __future__ import annotations
from typing import Optional, Union
import uuid
from arcgis.auth.tools import LazyLoader
import re

arcgis = LazyLoader("arcgis")
Content = LazyLoader("arcgis.apps.storymap.story_content")
StoryMap = LazyLoader("arcgis.apps.storymap.story")
Briefing = LazyLoader("arcgis.apps.storymap.briefing")
json = LazyLoader("json")
time = LazyLoader("time")

# ----------------------------------------------------------------------
def _get_thumbnail(gis) -> str:
    """
    Private method to get the default thumbnail path dependent on whether the
    user is Online or on Enterprise.
    """
    if gis._is_agol:
        thumbnail = "https://storymaps.arcgis.com/static/images/item-default-thumbnails/item.jpg"
    else:
        thumbnail = (
            gis._url
            + "/apps/storymaps/static/images/item-default-thumbnails/item.jpg"
        )
    return thumbnail

# ----------------------------------------------------------------------
def show(item, width: Optional[int] = None, height: Optional[int] = None):
    """
    Show a preview of the briefing. The default is a width of 700 and height of 300.

    ===============     ====================================================================
    **Parameter**       **Description**
    ---------------     --------------------------------------------------------------------
    width               Optional integer. The desired width to show the preview.
    ---------------     --------------------------------------------------------------------
    height              Optional integer. The desired height to show the preview.
    ===============     ====================================================================

    :return:
        An Iframe display of the briefing if possible, else the item url is returned to be
        clicked on.
    """
    try:
        if item:
            width = 700 if width is None else width
            height = 350 if height is None else height
            from IPython.display import IFrame

            return IFrame(
                src=item.url,
                width=width,
                height=height,
                params="title=" + item.title,
            )
    except:
        return item.url

# ----------------------------------------------------------------------
def cover(
    story,
    title: Optional[str] = None,
    type: str = None,
    summary: Optional[str] = None,
    by_line: Optional[str] = None,
    media: Optional[Union[Content.Image, Content.Video]] = None,
):
    """
    A briefing's cover is the first slide.
    This method allows the cover to be edited by updating the title, byline, image, and more.
    Changing one part of the briefing cover will not change the rest of the cover. If just the
    image is passed in then only the image will change.

    ===============     ====================================================================
    **Parameter**        **Description**
    ---------------     --------------------------------------------------------------------
    title               Optional string. The title of the Briefing cover.
    ---------------     --------------------------------------------------------------------
    type                Optional string. The type of briefing cover to be used in the story.

                        ``Values: "full" | "sidebyside" | "minimal"``
    ---------------     --------------------------------------------------------------------
    summary             Optional string. The description of the story.
    ---------------     --------------------------------------------------------------------
    by_line             Optional string. Crediting the author(s).
    ---------------     --------------------------------------------------------------------
    media               Optional url or file path or :class:`~arcgis.apps.storymap.story_content.Image` or
                        :class:`~arcgis.apps.storymap.story_content.Video` object.
    ===============     ====================================================================

    :return: True if the cover was updated successfully.

    .. code-block:: python

        briefing = Briefing(<briefing item>)
        briefing.cover(title="My Briefing Title", type="sidebyside", summary="My little summary", by_line="python_dev")
        briefing.save()

    """
    if isinstance(story, Briefing.Briefing):
        ui = story._properties["nodes"][story._properties["root"]][
            "children"
        ][0]
        story_cover_node = story._properties["nodes"][ui]["children"][0]

    # get original data of story cover
    orig_data = story._properties["nodes"][story_cover_node]["data"]

    # set the new values, if any
    story._properties["nodes"][story_cover_node] = {
        "type": "storycover",
        "data": {
            "type": orig_data["type"] if type is None else type,
            "title": orig_data["title"] if title is None else title,
            "summary": orig_data["summary"] if summary is None else summary,
            "byline": orig_data["byline"] if by_line is None else by_line,
            "titlePanelPosition": orig_data["titlePanelPosition"]
            if by_line is None
            else "start",
        },
    }

    # set the cover media
    if media is not None:
        if not isinstance(media, Content.Image) and not isinstance(media, Content.Video):
            raise ValueError("Media must be an image or video object. This was not updated")
        if media.node not in story._properties["nodes"]:
            # must be added to story resources
            if media._type == "image":
                media._add_image(story=story)
            else:
                media._add_video(story=story)
        story._properties["nodes"][story_cover_node]["children"] = [media.node]
    else:
        # get original image
        if "children" in story._properties["nodes"][story_cover_node]:
            media = story._properties["nodes"][story_cover_node]["children"][0]
            story._properties["nodes"][story_cover_node]["children"] = [media]

    return story._properties["nodes"][story_cover_node]

# ----------------------------------------------------------------------
def theme(story, theme: Union[StoryMap.Themes, str] = StoryMap.Themes.SUMMIT):
    """
    Each briefing has a theme node in its resources. This method can be used to change the theme.
    To add a custom theme to your story, pass in the item_id for the item of type Story Map Theme.

    ===============     ====================================================================
    **Parameter**        **Description**
    ---------------     --------------------------------------------------------------------
    theme               Required Themes Style or custom theme item id.
                        The theme to set on the briefing.

                        Values: `SUMMIT` | `TIDAL` | `MESA` | `RIDGELINE` | `SLATE` | `OBSIDIAN` | `<item_id>`
    ===============     ====================================================================

    .. code-block:: python

        >>> from arcgis.apps.storymap import Themes, Briefing

        >>> briefing = Briefing()
        >>> briefing.theme(Themes.TIDAL)
    """
    # find the node corresponding to the story theme in resources
    # the properties only holds the resource node id. If this doesn't change then don't need to update
    for node, node_info in story._properties["resources"].items():
        for key, val in node_info.items():
            if key == "type" and val == "story-theme":
                if isinstance(theme, StoryMap.Themes):
                    # theme comes from Themes class
                    story._properties["resources"][node]["data"][
                        "themeId"
                    ] = theme.value
                if isinstance(theme, str):
                    # theme is an item of type Story Theme
                    story._properties["resources"][node]["data"][
                        "themeItemId"
                    ] = theme
# ----------------------------------------------------------------------
def save(
    story,
    title: Optional[str] = None,
    tags: Optional[list] = None,
    access: str = None,
    publish: bool = False,
):
    """
    This method will save your Story Map to your active GIS. The story will be saved
    with unpublished changes unless `publish` parameter is specified to True.

    The title only needs to be specified if a change is wanted, otherwise exisiting title
    is used.

    .. warning::
        Publishing your story through the Python API means it will not go through the Story Map
        issue checker. It is recommended to publish through the Story Maps builder if you
        want your story to go through the issue checker.

    .. warning::
        Changes to the published story may not be visible for up to one hour. You can open
        the story in the story builder to force changes to appear immediately and perform
        other optimizations, such as updating the story's social/SEO metadata.

    ===============     ====================================================================
    **Parameter**        **Description**
    ---------------     --------------------------------------------------------------------
    title               Optional string. The title of the StoryMap.
    ---------------     --------------------------------------------------------------------
    tags                Optional string. The tags of the StoryMap.
    ---------------     --------------------------------------------------------------------
    access              Optional string. The access of the StoryMap. If none is specified, the
                        current access is kept. This is used when `publish` parameter is set
                        to True.

                        Values: `private` | `org` | `public`
    ---------------     --------------------------------------------------------------------
    publish             Optional boolean. If True, the story is saved and also published.
                        Default is false so story is saved with unpublished changes.
    ===============     ====================================================================


    :return: The Item that was saved to your active GIS.

    """
    # Remove old draft item
    for resource in story._resources:
        if re.match("draft_[0-9]{13}.json", resource["resource"]) or re.match(
            "draft.json", resource["resource"]
        ):
            _remove_resource(story, file=resource["resource"])

    # Add meta settings and change push meta so title doesn't get overwritten on publish at any point.
    # if title:
    #     root = story._properties["root"]
    #     if "metaSettings" not in story._properties["nodes"][root]["data"]:
    #         story._properties["nodes"][root]["data"]["metaSettings"] = {
    #             "title": None
    #         }
    #     story._properties["nodes"][root]["data"]["metaSettings"]["title"] = title
    #     if "config" not in story._properties["nodes"][root]:
    #         story._properties["nodes"][root]["config"] = {}
    #     story._properties["nodes"][root]["config"][
    #         "shouldPushMetaToAGOItemDetails"
    #     ] = False

    # Add new draft with time in milliseconds
    draft = "draft_" + str(int(time.time() * 1000)) + ".json"
    json_str = json.dumps(story._properties, ensure_ascii=False)
    _add_resource(story, resource_name=draft, text=json_str, access="private")
    # get the story map version from endpoint
    sm_version = story._gis._con.get("https://storymaps.arcgis.com/version")[
        "version"
    ]
    # Find type keywords to use based on whether to publish or not
    if isinstance(story, Briefing.Briefing):
        briefing_keywords = [
            "alphabriefing",
            "storymapbriefing"]
        
    # PUBLISH MODE
    if publish is True:
        # Remove old publish item
        for resource in story._resources:
            if (
                "publish_data" in resource["resource"]
                or "published_data" in resource["resource"]
                or "publish" in resource["resource"]
            ):
                _remove_resource(story, file=resource["resource"])
        # Add new publish
        _add_resource(
            story, resource_name="published_data.json", text=json.dumps(story._properties)
        )
        # Set the keywords
        # Start by getting the existing keywords and remove what will be replaced
        keywords = story._item.typeKeywords
        if "smstatusunpublishedchanges" in keywords:
            # changing to publish after
            idx = keywords.index("smstatusunpublishedchanges")
            del keywords[idx]
        if "smstatusdraft" in keywords:
            idx = keywords.index("smstatusdraft")
            del keywords[idx]
        for keyword in keywords:
            # iterate through since only know part of keyword we want to remove
            if (
                "smdraftresourceid"
                or "smpublisheddate"
                or "smstatusdraft"
                or "smpublisherapp"
            ) in keyword:
                keywords.remove(keyword)
        new_keywords = [
            "smstatuspublished",
            "smversiondraft:" + sm_version,
            "smversionpublished:" + sm_version,
            "python-api",
            "smpublisherapp:python-api-" + arcgis.__version__,
            "smdraftresourceid:" + draft,
            "smpublisheddate:" + str(int(time.time() * 1000)),
        ]
        if isinstance(story, Briefing.Briefing):
            new_keywords = new_keywords + briefing_keywords
        # Setting the keywords in a set will remove duplicates
        p = {
            "typeKeywords": list(set(keywords + new_keywords)),
            "text": json.dumps(story._properties),
            "url": story._url,
        }
        if title:
            p["title"] = title
        if tags:
            p["tags"] = tags

        # Find and set access
        sharing = access if access is not None else story._item.access
        p["access"] = sharing

        # Update the item and invoke share to have correct access
        story._item.update(item_properties=p)

        if sharing == "private":
            story._item.share(everyone=False, org=False, groups=None)
        elif sharing == "org":
            story._item.share(org=True)
        elif sharing == "public":
            story._item.share(everyone=True)

        if (
            story._gis._con._session.auth
            and story._gis._con._session.auth.token is not None
        ):
            # Make a call to the StoryMaps publish endpoint
            story._gis._con.post(
                path=story._url + "/publish",
                params={"f": "json", "token": story._gis._con._session.auth.token},
            )
    else:
        # Set the type keywords
        keywords = story._item.typeKeywords
        previously_published = False
        for keyword in keywords:
            if "smpublisheddate" in keyword:
                # Update the date in new keywords
                previously_published = True
                keywords.remove(keyword)
            elif (
                "smstatuspublished" in keyword
                or "smstatusdraft" in keyword
                or "smdraftresourceid" in keyword
                or "smeditorapp" in keyword
                or "Copy Item" in keyword
            ):
                # Remove old keywords and will be replaced in new keywords
                keywords.remove(keyword)
        if previously_published is True:
            # Unpublished changes mode
            new_keywords = [
                "smstatusunpublishedchanges",
                "smversiondraft:" + sm_version,
                "python-api",
                "smeditorapp:python-api-" + arcgis.__version__,
                "smdraftresourceid:" + draft,
                "smversionpublished:" + sm_version,
                "smpublisheddate:" + str(int(time.time() * 1000)),
            ]
        if previously_published is False:
            # Draft mode
            new_keywords = [
                "smstatusdraft",
                "smversiondraft:" + sm_version,
                "python-api",
                "smeditorapp:python-api-" + arcgis.__version__,
                "smdraftresourceid:" + draft,
            ]
        if isinstance(story, Briefing.Briefing):
            new_keywords = new_keywords + briefing_keywords
        # Pass through set first to remove duplicates
        p = {"typeKeywords": list(set(keywords + new_keywords))}
        if title:
            p["title"] = title
        if tags:
            p["tags"] = tags
        # access does not change when only saving
        p["access"] = story._item.access
        story._item.update(item_properties=p)

    story._item = story._gis.content.get(story._itemid)
    return story._item

# ----------------------------------------------------------------------
def delete_briefing(story):
    """
    Deletes the briefing item.
    """
    # Check if item id exists
    item = story._gis.content.get(story._itemid)
    return item.delete()
# ----------------------------------------------------------------------
def duplicate(story, title: Optional[str] = None):
    """
    Duplicate the story. All items will be duplicated as they are. This allows you to create
    a briefing template and duplicate it when you want to work with it.

    It is highly recommended that once the duplicate is created, open it in StoryMap Briefing
    builder to ensure the issue checker finds any issues before editing.

    .. note::
        Can be used with ArcGIS Online or with ArcGIS Enterprise starting 10.8.1.
    
    .. note::
        To duplicate into another organization, use the :func:`~arcgis.gis.ContentManager.clone_items` method.

    ===============     ====================================================================
    **Parameter**        **Description**
    ---------------     --------------------------------------------------------------------
    title               Optional string. The title of the duplicated story. Only availble
                        for ArcGIS Online.
    ===============     ====================================================================

    :return:
        The Item that was created.

    .. code-block:: python

        # Example for ArcGIS Online
        >>> briefing = Briefing(<briefing item>)
        >>> briefing.duplicate("A Briefing Copy")
    """
    # get the item to copy
    item = story._gis.content.get(story._itemid)

    # enterprise copy_item starting at 10.8.1
    if item._portal.is_arcgisonline is False and story._gis.version < [8, 2]:
        clone = story._gis.content.clone_items(items=[item])
    else:
        clone = item.copy_item(
            title="(Copy) " + story._item.title if title is None else title,
            include_resources=True,
            include_private=True,
        )
    # save to update keywords
    clone_story = Briefing(clone.id)
    return clone_story.save()

# ----------------------------------------------------------------------
def get(story, node: Optional[str] = None, type: Optional[str] = None):
    """
    Get node(s) by type or by their id. Using this function will help grab a specific node
    from the story if a node id is provided. Set this to a variable and this way edits can be
    made on the node in the story.

    ===============     ====================================================================
    **Parameter**        **Description**
    ---------------     --------------------------------------------------------------------
    node                Optional string. The node id for the node that should be returned.
                        This will return the class of the node if of type story content.
    ---------------     --------------------------------------------------------------------
    type                Optional string. The type of nodes that user wants returned.
                        If none specified, list of all nodes returned.


                        Values: `image` | `video` | `audio` | `embed` | `webmap` | `text` |
                        `button` | `separator` | `expressmap` | `webscene` | `immersive`
    ===============     ====================================================================

    :return:
        If type specified: List of node ids and their types in order of appearance in the story map.

        If node_id specified: The node itstory.


    .. code-block:: python

        >>> story = StoryMap(<story item>)

        # Example get by type
        >>> story.get(type = "text")
        Returns a list of all nodes of type text

        # Example by id
        >>> text = story.get(node= "<id for text node>")
        >>> text.properties
        Returns a specific node of type text

    """
    spec_type = []
    node_id = node
    if node_id and node_id not in story._properties["nodes"]:
        raise ValueError(
            "This node value is not in the story. "
            + "Please check that you have entered the correct node id. "
            + "To see all main nodes and their ids use the nodes property."
        )
    if type is None and node_id is None:
        # return all nodes in order
        return story.nodes
    elif node_id is not None:
        # check first if it's an action
        all_actions = story.actions
        for action in all_actions:
            id = list(action.keys())[0]
            if node_id == id:
                return list(action.values())[0]
        # return a specific node
        all_nodes = _create_node_dict(story)
        # find the node in the list and return it
        for node in all_nodes:
            id = list(node.keys())[0]
            if node_id == id:
                return list(node.values())[0]
    else:
        # return all nodes of a certain type
        all_nodes = _create_node_dict(story)
        for node in all_nodes:
            keyword = str(list(node.values())[0]).lower()
            if isinstance(keyword, str):
                # Not a type of story content (i.e. navigation)
                if type.lower() in keyword:
                    spec_type.append(node)
            else:
                # Find all story content instances (i.e. Text)
                # Map types are upercase and have spaces so handle
                if type.lower() in keyword._type.lower().replace(" ", ""):
                    spec_type.append(node)
        return spec_type

# ----------------------------------------------------------------------
def _has_children(story, node):
    """
    Check if node has children and return list of children else None.
    """
    node_class = _assign_node_class(story, node)
    if (
        isinstance(node_class, Content.Sidecar)
        or isinstance(node_class, Content.Gallery)
        or isinstance(node_class, Content.Timeline)
    ):
        return story._properties["nodes"][node]["children"]
    elif isinstance(node_class, Content.Swipe):
        return list(story._properties["nodes"][node]["data"]["contents"].values())
    elif isinstance(node_class, Content.MapTour):
        mt = get(node)
        return mt._children
    elif isinstance(node_class, str):
        if (
            "immersive" in node_class.lower()
            or "credits" in node_class.lower()
            or "event" in node_class.lower()
            or "carousel" in node_class.lower()
        ):
            return (
                story._properties["nodes"][node]["children"]
                if "children" in story._properties["nodes"][node]
                else None
            )
    else:
        return None

# ----------------------------------------------------------------------
def _delete(story, node_id):
    # Check if node is in story
    if node_id not in story._properties["nodes"]:
        return False

    # Get list of nodes in the story
    root_id = story._properties["root"]
    children = story._properties["nodes"][root_id]["children"]

    # Remove from children of story
    if node_id in children:
        story._properties["nodes"][root_id]["children"].remove(node_id)
    # Remove from nodes dictionary
    del story._properties["nodes"][node_id]
    # Remove node from any immersive nodes.
    # A node can belong to an immersive narrative panel or an immersive slide
    for node in story._properties["nodes"]:
        if (
            "immersive" in story._properties["nodes"][node]["type"]
            and "children" in story._properties["nodes"][node]
        ):
            for child in story._properties["nodes"][node]["children"]:
                # iterate through children to see if node is part of it
                if child == node_id:
                    story._properties["nodes"][node]["children"].remove(node_id)

    return True

# ----------------------------------------------------------------------
def _add_child(story, node_id, position=None):
    """
    A story node has children. Children is a list of item nodes that are in
    the story. The order of the list determines the order that the nodes
    appear in the story. First and last nodes are reserved for story_cover
    and credits. The second node is always navigation. If visible is not set
    to True is simply won't be seen but stays in position 2.
    """
    # Get list of children in story
    root_id = story._properties["root"]

    if isinstance(story, Briefing.Briefing):
        # for briefings, the only child is the ui
        # the ui node has the slides
        principal_id = story._properties["nodes"][root_id]["children"][0]
    else:
        # for storymap the children are the root
        principal_id = root_id
    last = len(story._properties["nodes"][principal_id]["children"]) - 1

    if position and position < last and position != 0 and position != 1:
        # If the position adheres to rules then add node
        story._properties["nodes"][principal_id]["children"].insert(position, node_id)
    elif position and (position == 0 or position == 1):
        # First and second node reserved for story cover and navigation
        # Add as third node if user specified position 0 or 1
        story._properties["nodes"][principal_id]["children"].insert(2, node_id)
    else:
        # Last node is reserved for credits so add before this if user wanted last position
        story._properties["nodes"][principal_id]["children"].insert(last, node_id)

# ----------------------------------------------------------------------
def _add_resource(story, file=None, resource_name=None, text=None, access="inherit"):
    """
    See :class:`~arcgis.gis.ResourceManager`
    """
    resource_manager = arcgis.gis.ResourceManager(story._item, story._gis)
    is_present = False
    if file:
        for resource in story._resources:
            if resource["resource"] in file:
                is_present = True
                resp = True
    properties = {
        "editInfo": {
            "editor": story._gis._username,
            "modified": str(int(time.time() * 1000)),
            "id": uuid.uuid4().hex[0:21],
            "app": "python-api",
        }
    }

    # access is inherited from item upon add, except for json where always private
    if is_present is False:
        resp = resource_manager.add(
            file=file,
            file_name=resource_name,
            text=text,
            access=access,
            properties=properties,
        )

    story._resources = story._item.resources.list()
    return resp

# ----------------------------------------------------------------------
def _remove_resource(story, file=None):
    """
    See :class:`~arcgis.gis.ResourceManager`
    """
    try:
        resource_manager = arcgis.gis.ResourceManager(story._item, story._gis)
        resp = resource_manager.remove(file=file)
        story._resources = story._item.resources.list()
        return resp
    except:
        # Resource cannot be found. Should not throw error
        return True

# ----------------------------------------------------------------------
def _assign_node_class(story, node_id):
        # Find the node type to assign to correct class
        node_type = story._properties["nodes"][node_id]["type"]
        # Create an instance of this class using existing node properties
        if node_type == "separator":
            node = Content.Separator(story=story, node_id=node_id)
        elif node_type == "briefing-slide":
            node = Content.Slide(story=story, node_id=node_id)
        elif node_type == "image":
            node = Content.Image(story=story, node_id=node_id)
        elif node_type == "video":
            node = Content.Video(story=story, node_id=node_id)
        elif node_type == "audio":
            node = Content.Audio(story=story, node_id=node_id)
        elif node_type == "embed":
            # embed has subtype: video or link
            subtype = story._properties["nodes"][node_id]["data"]["embedType"]
            if subtype == "video":
                node = Content.Video(story=story, node_id=node_id)
            else:
                node = Content.Embed(story=story, node_id=node_id)
        elif node_type == "webmap":
            node = Content.Map(story=story, node_id=node_id)
        elif node_type == "text":
            node = Content.Text(story=story, node_id=node_id)
        elif node_type == "button":
            node = Content.Button(story=story, node_id=node_id)
        elif node_type == "swipe":
            node = Content.Swipe(story=story, node_id=node_id)
        elif node_type == "gallery":
            node = Content.Gallery(story=story, node_id=node_id)
        elif node_type == "timeline":
            node = Content.Timeline(story=story, node_id=node_id)
        elif node_type == "tour":
            node = Content.MapTour(story=story, node_id=node_id)
        elif node_type == "immersive":
            # immersive has subtype sidecar (more to add later)
            subtype = story._properties["nodes"][node_id]["data"]["type"]
            if subtype == "sidecar":
                node = Content.Sidecar(story=story, node_id=node_id)
            else:
                node = subtype
        elif node_type == "action-button":
            node = Content.MapAction(story=story, node_id=node_id)
        else:
            # if not of type story content then just return name of type
            node = node_type.capitalize()
        return node

# ----------------------------------------------------------------------
def _create_node_dict(story):
    """
    Method called by the nodes property and the get method. However, the nodes
    property will transform the keys whereas the get method needs they keys
    to be class instances.
    """
    # get rood node id since it is story node id
    root_id = story._properties["root"]
    # get list of children from story node
    if isinstance(story, Briefing.Briefing):
        ui = story._properties["nodes"][root_id]["children"]
        children = story._properties["nodes"][ui[0]]["children"]
    else:
        children = story._properties["nodes"][root_id]["children"]
    nodes = story._properties["nodes"]

    node_order = []
    # for each node assign correct class type to be accessed if needed by user
    for child in children:
        # get only the main nodes and not the subnodes to be returned
        if child in nodes:
            node = _assign_node_class(story, child)
            node_order.append({child: node})
    return node_order