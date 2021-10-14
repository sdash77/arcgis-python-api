import os
import time
import json
import mimetypes
from typing import Optional, Union
from arcgis import env
from arcgis.gis import Item
import uuid
from PIL import Image


class StoryMap(object):
    """
    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    story_item             Optional :class:`~arcgis.gis.Item` object whose Item.type is ``Story Map``.

                           .. note::
                            If not specified,
                            an empty ``StoryMap`` object is created with some useful defaults.

    ==================     ====================================================================

    """

    _properties = None
    _gis = None
    _itemid = None
    _item = None

    def __init__(self, item=None, gis=None):
        """initializer"""
        if gis is None:
            self._gis = env.active_gis
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
            itemid = str(uuid.uuid4())
            properties = {
                "root": "n-gV3vrF",
                "nodes": {
                    "n-EW4IPO": {
                        "type": "navigation",
                        "config": {"isHidden": True},
                        "data": {"links": []},
                    },
                    "n-HlewXM": {"type": "credits"},
                    "n-JOB9tP": {
                        "type": "storycover",
                        "data": {
                            "byline": self._gis.properties.user.fullName,
                            "summary": "",
                            "title": "New Story",
                            "titlePanelPosition": "start",
                            "type": "minimal",
                        },
                    },
                    "n-gV3vrF": {
                        "type": "story",
                        "data": {"storyTheme": "r-JJKYN8"},
                        "config": {"coverDate": "first-published"},
                        "children": ["n-JOB9tP", "n-EW4IPO", "n-HlewXM"],
                    },
                },
                "resources": {
                    "r-JJKYN8": {
                        "type": "story-theme",
                        "data": {"themeId": "summit", "themeBaseVariableOverrides": {}},
                    }
                },
            }
            self._itemid = itemid
            self._properties = properties

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
        """returns the storymap's JSON"""
        return self._properties

    # ----------------------------------------------------------------------
    def add_media(
        self,
        item: Union[str, Item],
        caption: str = "",
        alt_text: str = "",
        display: str = "float",
        position: Optional[int] = None,
        **kwargs,
    ):
        """
        Add media content to a ```Story Map```.

        The types of content that can be added are: Map, Image, Video, Audio, or Embed.

        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        item                    Optional :class:`~arcgis.gis.Item` that is of type ```WebMap```,
                                url, or file path. Url and file path are passed as a String.

                                .. note::
                                Depending on the item you want to add, different parameters can be passed in.
                                Please refer to the documentation.
        ------------------      --------------------------------------------------------------------
        title
        ------------------      --------------------------------------------------------------------
        caption
        ------------------      --------------------------------------------------------------------
        alt_text
        ------------------      --------------------------------------------------------------------
        display                 Optional String. The display size of the item in the story.

                                Values: “small” | “wide” | “full” | “float” (default)
        ==================      ====================================================================
        """
        if isinstance(item, Item):
            show_legend = kwargs.pop("show_legend", False)
            show_default_legend = kwargs.pop("show_default_legend", False)
            extent = kwargs.pop("extent", None)
            layer_visibility = kwargs.pop("layer_visibility", None)
            popup = kwargs.pop("popup", None)
            if layer_visibility:
                layer_visibility = json.dumps(layer_visibility)
            return self._add_webmap(
                item=item,
                caption=caption,
                alt_text=alt_text,
                display=display,
                show_legend=show_legend,
                show_default_legend=show_default_legend,
                extent=extent,
                layer_visibility=layer_visibility,
                popup=popup,
            )
        elif isinstance(item, str):
            mt = mimetypes.guess_type(item)[0].lower()
            if "video" in mt:
                return self._add_video(
                    item=item,
                    caption=caption,
                    alt_text=alt_text,
                    display=display,
                    position=position,
                )
            elif "image" in mt:
                return self._add_image(
                    item=item,
                    caption=caption,
                    alt_text=alt_text,
                    display=display,
                    ext_type=mt,
                    position=position,
                )
            elif "audio" in mt:
                return self._add_audio(
                    item=item,
                    caption=caption,
                    alt_text=alt_text,
                    display=display,
                    ext_type=mt,
                    position=position,
                )
            else:
                # An Embed or Web Scene
                return self._add_webpage(
                    item=item,
                    caption=caption,
                    alt_text=alt_text,
                    display=display,
                    ext_type=mt,
                    position=position,
                )
        return False

    # ----------------------------------------------------------------------
    def _add_webmap(
        self, item, caption="", alt_text="", display="float", position=None,
    ):
        """
        Adds a webmap to the storymap

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Required string. The title of the section.
        ---------------     --------------------------------------------------------------------
        url                 Required string. The web address of the webpage
        ---------------     --------------------------------------------------------------------
        caption             Optional string. The caption of the section.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional string. Specifies an alternate text for an image.
        ---------------     --------------------------------------------------------------------
        display             Optional string. The image display properties.
        ---------------     --------------------------------------------------------------------
        ext_type            The image extention type
        ---------------     --------------------------------------------------------------------
        position            Optional int. Will position the element in the story list.
        ===============     ====================================================================


        :return: Boolean

        """
        # Create ids
        node_id = "n-" + uuid.uuid4().hex[0:6]
        resource_node = "r-" + uuid.uuid4().hex[0:6]

        # Create webmap nodes
        self.properties["nodes"][node_id] = {
            "type": "webmap",
            "data": {
                "map": resource_node,
                "caption": caption,
                "alt": alt_text,
                "mapLayers": item.layers,
                "extent": item.extent,
                "center": item.center,
                "zoom": item.zoom,
                "viewpoint": item.viewpoint,
            },
            "config": {"size": display,},
        }

        # Create resource node
        self.properties["resources"][resource_node] = {
            "type": "webmap",
            "data": {
                "extent": item.extent,
                "center": item.center,
                "zoom": item.zoom,
                "viewpoint": item.viewpoint,
                "mapLayers": item.layers,
                "itemId": item.id,
                "itemType": "Web Map",
                "type": "default",
            },
        }

        # Add to story children, position counts
        root_id = self.properties["root"]
        if position:
            self.properties["nodes"][root_id]["children"][position] = node_id
        else:
            self.properties["nodes"][root_id]["children"] = node_id

    # ----------------------------------------------------------------------
    def _add_video(
        self,
        item,
        caption="",
        alt_text="",
        display="float",
        ext_type="mp4",
        position=None,
    ):
        """
        Adds a video to the storymap

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Required string. The title of the section.
        ---------------     --------------------------------------------------------------------
        url                 Required string. The web address of the webpage
        ---------------     --------------------------------------------------------------------
        caption             Optional string. The caption of the section.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional string. Specifies an alternate text for an image.
        ---------------     --------------------------------------------------------------------
        display             Optional string. The image display properties.
        ---------------     --------------------------------------------------------------------
        ext_type            The image extention type
        ---------------     --------------------------------------------------------------------
        position            Optional int. Will position the element in the story list.
        ===============     ====================================================================


        :return: Boolean

        """
        # Create ids
        node_id = "n-" + uuid.uuid4().hex[0:6]
        resource_node = "r-" + uuid.uuid4().hex[0:6]
        resource_id = str(int(time.time())) + "." + ext_type

        # Add resource
        self._add_resouce(item, resource_id)

        # Create video nodes
        self.properties["nodes"][node_id] = {
            "type": "video",
            "data": {"video": resource_node, "caption": caption, "alt": alt_text},
            "config": {"size": display,},
        }

        # Create resource node
        self.properties["resources"][resource_node] = {
            "type": "video",
            "data": {"resourceId": resource_id, "provider": "item-resource",},
        }

        # Add to story children, position counts
        root_id = self.properties["root"]
        if position:
            self.properties["nodes"][root_id]["children"][position] = node_id
        else:
            self.properties["nodes"][root_id]["children"] = node_id

    # ----------------------------------------------------------------------
    def _add_image(
        self,
        item,
        caption="",
        alt_text="",
        display="float",
        ext_type="image/jpeg",
        position=None,
    ):
        """
        Adds an image to the storymap

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Required string. The title of the section.
        ---------------     --------------------------------------------------------------------
        url                 Required string. The web address of the webpage
        ---------------     --------------------------------------------------------------------
        caption             Optional string. The caption of the section.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional string. Specifies an alternate text for an image.
        ---------------     --------------------------------------------------------------------
        display             Optional string. The image display properties.
        ---------------     --------------------------------------------------------------------
        ext_type            The image extention type
        ---------------     --------------------------------------------------------------------
        position            Optional int. Will position the element in the story list.
        ===============     ====================================================================


        :return: Boolean

        """

        # Create ids
        node_id = "n-" + uuid.uuid4().hex[0:6]
        resource_node = "r-" + uuid.uuid4().hex[0:6]

        ext_type = ext_type.split("/")
        resource_id = str(int(time.time())) + "." + ext_type[1]

        # Add resource
        self._add_resource(item, resource_id)

        # Create image nodes
        self.properties["nodes"][node_id] = {
            "type": "image",
            "data": {"image": resource_node, "caption": caption, "alt": alt_text},
            "config": {"size": display,},
        }

        im = Image.open(item)
        w, h = im.size
        # Create resource node
        self.properties["resources"][resource_node] = {
            "type": "image",
            "data": {
                "resourceId": resource_id,
                "provider": "item-resource",
                "height": h,
                "width": w,
            },
        }

        # Add to story children, position counts
        root_id = self.properties["root"]
        if position:
            self.properties["nodes"][root_id]["children"][position] = node_id
        else:
            self.properties["nodes"][root_id]["children"] = node_id

    # ----------------------------------------------------------------------
    def _add_audio(
        self,
        item,
        caption="",
        alt_text="",
        display="float",
        ext_type="audio/mp3",
        position=None,
    ):
        """
        Adds an audio to the storymap

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Required string. The title of the section.
        ---------------     --------------------------------------------------------------------
        url                 Required string. The web address of the webpage
        ---------------     --------------------------------------------------------------------
        caption             Optional string. The caption of the section.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional string. Specifies an alternate text for an image.
        ---------------     --------------------------------------------------------------------
        display             Optional string. The image display properties.
        ---------------     --------------------------------------------------------------------
        ext_type            The image extention type
        ---------------     --------------------------------------------------------------------
        position            Optional int. Will position the element in the story list.
        ===============     ====================================================================


        :return: Boolean

        """
        # Create ids
        node_id = "n-" + uuid.uuid4().hex[0:6]
        resource_node = "r-" + uuid.uuid4().hex[0:6]

        ext_type = ext_type.split("/")
        resource_id = str(int(time.time())) + "." + ext_type[1]

        # Add resource
        self._add_resouce(item, resource_id)

        # Create image nodes
        self.properties["nodes"][node_id] = {
            "type": "audio",
            "data": {"video": resource_node, "caption": caption, "alt": alt_text},
            "config": {"size": display,},
        }

        # Create resource node
        self.properties["resources"][resource_node] = {
            "type": "audio",
            "data": {"resourceId": resource_id, "provider": "item-resource",},
        }

        # Add to story children, position counts
        root_id = self.properties["root"]
        if position:
            self.properties["nodes"][root_id]["children"][position] = node_id
        else:
            self.properties["nodes"][root_id]["children"] = node_id

    # ----------------------------------------------------------------------
    def _add_webpage(
        self,
        item,
        caption="",
        alt_text="",
        display="float",
        ext_type="",
        position=None,
    ):
        """
        Adds a webpage to the storymap

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Required string. The title of the section.
        ---------------     --------------------------------------------------------------------
        url                 Required string. The web address of the webpage
        ---------------     --------------------------------------------------------------------
        caption             Optional string. The caption of the section.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional string. Specifies an alternate text for an image.
        ---------------     --------------------------------------------------------------------
        display             Optional string. The image display properties.
        ---------------     --------------------------------------------------------------------
        ext_type            The image extention type
        ---------------     --------------------------------------------------------------------
        position            Optional int. Will position the element in the story list.
        ===============     ====================================================================


        :return: Boolean

        """
        # Create ids
        node_id = "n-" + uuid.uuid4().hex[0:6]
        resource_node = "r-" + uuid.uuid4().hex[0:6]

        # Create embed nodes
        self.properties["nodes"][node_id] = {
            "type": "embed",
            "data": {"embed": resource_node, "caption": caption, "alt": alt_text},
            "config": {"size": display,},
        }

        # Create resource node
        self.properties["resources"][resource_node] = {
            "type": "embed",
            "data": {"resourceId": str(int(time.time())) + ext_type},
        }

        # Add to story children, position counts
        root_id = self.properties["root"]
        if position:
            self.properties["nodes"][root_id]["children"][position] = node_id
        else:
            self.properties["nodes"][root_id]["children"] = node_id

    # ----------------------------------------------------------------------
    def _add_resource(
        self, file=None, resource_id=None,
    ):
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

        params = {}
        params["f"] = "json"
        params["fileName"] = resource_id
        params["access"] = self._item.access
        resp = self._gis._portal.con.post(url, params, files=files, compress=False)
        return resp

