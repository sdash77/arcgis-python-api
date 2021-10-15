import os
import time
import json
import mimetypes
from typing import Optional, Union
from arcgis import env
from arcgis.gis import GIS, Item
import uuid
from PIL import Image
from urllib.parse import urlparse


# TODO:
# Save story map function
# Update story map function
# Publish story map function
# Edit media item (do they specify node?). Also do we delete and repost resource ? What about position.
# Edit text, button, and separator (text for text and button , position, etc.)


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
            f = open("templates\data.json",)
            self._properties = json.load(f)
            self._itemid = str(uuid.uuid4())
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
        """returns the storymap's JSON"""
        return self._properties

    # ----------------------------------------------------------------------
    @property
    def node_order(self):
        """returns the storymap's node order"""
        root_id = self.properties["root"]
        children = self.properties["nodes"][root_id]["children"]
        return children

    # ----------------------------------------------------------------------
    def add_text(
        self,
        text: str,
        type: str = "paragraph",
        custom_color: str = "000",
        position: Optional[int] = None,
    ):
        """
        Add text to a ```Story Map```

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
        ------------------      --------------------------------------------------------------------
        position                Optional int. Determines where the text will be placed in the story.
                                Default is at the end.
        ==================      ====================================================================        
        """
        # Create ids
        node_id = uuid.uuid4().hex[0:6]

        self.properties["nodes"][node_id] = {
            "type": "text",
            "data": {"type": type, "text": text, "customTextColors": [custom_color]},
        }

        # Add to story children, position counts
        self._add_child(node_id=node_id, position=position)

    # ----------------------------------------------------------------------
    def add_button(self, link: str, text: str, position: Optional[int] = None):
        """
        Adds a button node to the Story Map. A button has a link associated to it.

        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        link                    Required String. When user clicks on button, they will be brought to
                                the link.
        ------------------      --------------------------------------------------------------------
        text                    Required String. The text that shows on the button.
        ------------------      --------------------------------------------------------------------
        position                Optional Integer. Determines where the button will be placed in the
                                story. The default is at the end.
        ==================      ====================================================================
        """
        # Create ids
        node_id = uuid.uuid4().hex[0:6]

        self.properties["nodes"][node_id] = {
            "type": "button",
            "data": {"text": text, "link": link},
        }

        # Add to story children, position counts
        self._add_child(node_id=node_id, position=position)

    # ----------------------------------------------------------------------
    def add_separator(self, position: Optional[int] = None):
        """
        Adds a separator node to the Story Map. 

        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        position                Optional Integer. Determines where the button will be placed in the
                                story. The default is at the end.
        ==================      ====================================================================
        """
        # Create ids
        node_id = uuid.uuid4().hex[0:6]

        self.properties["nodes"][node_id] = {
            "type": "separator",
        }

        # Add to story children, position counts
        self._add_child(node_id=node_id, position=position)

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
                                Depending on the item you want to add, different parameters can 
                                be passed in.
                                Please refer to the documentation.
        ------------------      --------------------------------------------------------------------
        caption                 Optional String. A caption for the media item for descriptive purpose.
        ------------------      --------------------------------------------------------------------
        alt_text                Optional String. Add text for screen reader a11y of the media.
        ------------------      --------------------------------------------------------------------
        display                 Optional String. The display size of the item in the story.

                                Values: “small” | “wide” | “full” | “float” (default)
        ------------------      --------------------------------------------------------------------
        position                Optional Integer. Determines the position of the item in the story.
                                The default is last position.
        ==================      ====================================================================


        **kwargs are used for adding a Web Map Item
        ==================      ====================================================================
        **Argument**            **Description**
        ------------------      --------------------------------------------------------------------
        show_legend             Optional Boolean. If True, map legend is shown. The default is False.
        ------------------      --------------------------------------------------------------------
        extent                  Optional Dictionary. 
                                
                                Example: 
                                extent = {
                                    "xmin": -9177882,
                                    "ymin": 4246761,
                                    "xmax": -9176720,
                                    "ymax": 4247967,
                                    "spatialReference": { "wkid": 102100 }
                                    }
        ------------------      --------------------------------------------------------------------
        center                  Optional List of two integers. 

                                Example:
                                center = [-112, 38]
        ------------------      --------------------------------------------------------------------
        zoom                    Optional Integer. The zoom level of the map.
        ------------------      --------------------------------------------------------------------
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
        ------------------      --------------------------------------------------------------------
        layer_visibility        Optional List of Dictionaries. The visibility of the layers in a webmap.  
                                
                                Syntax:

                                 [
                                    {
                                       "id" : "<layer_id>",
                                       "visibility" : "<true/false>"
                                    }
                                 ]
        ==================      ====================================================================

        """
        if isinstance(item, Item):
            show_legend = kwargs.pop("show_legend", False)
            extent = kwargs.pop("extent", None)
            if extent is None and "extent" in item:
                extent = {
                    "xmin": item.extent[0][0],
                    "xmax": item.extent[1][0],
                    "ymin": item.extent[0][1],
                    "ymax": item.extent[1][1],
                }
            center = kwargs.pop("center", None)
            zoom = kwargs.pop("zoom", None)
            viewpoint = kwargs.pop("viewpoint", None)
            if viewpoint:
                viewpoint = json.dumps(viewpoint)
            layer_visibility = kwargs.pop("layer_visibility", None)
            if layer_visibility:
                layer_visibility = json.dumps(layer_visibility)
            return self._add_webmap(
                item=item,
                caption=item.title if not caption else caption,
                alt_text=alt_text,
                display=display,
                position=position,
                show_legend=show_legend,
                extent=extent,
                center=center,
                zoom=zoom,
                viewpoint=viewpoint,
                layer_visibility=layer_visibility,
            )
        elif isinstance(item, str):
            mt = mimetypes.guess_type(item)[0].lower()
            if "video" in mt:
                return self._add_video(
                    item=item,
                    caption=caption,
                    alt_text=alt_text,
                    display=display,
                    ext_type=mt,
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
                    item=item, caption=caption, alt_text=alt_text, position=position,
                )
        return False

    # ----------------------------------------------------------------------
    def _add_webmap(
        self,
        item,
        caption,
        alt_text,
        display,
        position,
        show_legend,
        extent,
        center,
        zoom,
        viewpoint,
        layer_visibility,
    ):
        """
        Adds a webmap to the storymap

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        item                Web Map item to add to the story map.
        ---------------     --------------------------------------------------------------------
        caption             Optional string. The caption of the section.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional string. Specifies an alternate text for an image.
        ---------------     --------------------------------------------------------------------
        display             Optional string. The image display properties.
        ---------------     --------------------------------------------------------------------
        position            Optional int. Will position the element in the story list.
        ===============     ====================================================================


        :return: Boolean

        """
        # Create ids
        node_id = "n-" + uuid.uuid4().hex[0:6]
        resource_node = "r-" + item.id

        # Add resource
        self._add_resource(item, resource_node)

        # Create layer dictionary if None
        if layer_visibility is None and "layers" in item:
            layer_visibility = []
            for layer in item.layers:
                layer_item = {
                    "id": layer.properties.id,
                    "title": layer.properties.name,
                    "visibility": True,
                }
                layer_visibility.append(layer_item)

        # Create webmap nodes
        self.properties["nodes"][node_id] = {
            "type": "webmap",
            "data": {
                "map": resource_node,
                "caption": caption,
                "alt": alt_text,
                "mapLayers": layer_visibility,
                "extent": extent,
                "center": center,
                "zoom": zoom,
                "viewpoint": viewpoint,
                "showLegend": show_legend,
            },
            "config": {"size": display},
        }

        # Create resource node
        self.properties["resources"][resource_node] = {
            "type": "webmap",
            "data": {
                "extent": extent,
                "center": center,
                "zoom": zoom,
                "viewpoint": viewpoint,
                "mapLayers": layer_visibility,
                "itemId": item.id,
                "itemType": "Web Map",
                "type": "default",
                "showLegend": show_legend,
            },
        }

        # Add to story children, position counts
        self._add_child(node_id=node_id, position=position)

    # ----------------------------------------------------------------------
    def _add_video(
        self, item, caption, alt_text, display, ext_type, position=None,
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
        resource_id = str(int(time.time())) + ".mp4"

        # Add resource
        self._add_resource(item, resource_id)

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
        self._add_child(node_id=node_id, position=position)

    # ----------------------------------------------------------------------
    def _add_image(
        self, item, caption, alt_text, display, ext_type, position,
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
        self._add_child(node_id=node_id, position=position)

    # ----------------------------------------------------------------------
    def _add_audio(
        self, item, caption, alt_text, display, ext_type, position,
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
        self._add_resource(item, resource_id)

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
        self._add_child(node_id=node_id, position=position)

    # ----------------------------------------------------------------------
    def _add_webpage(
        self, item, caption, alt_text, position=None,
    ):
        """
        Adds a webpage to the storymap

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        item                Required string. The web address of the webpage
        ---------------     --------------------------------------------------------------------
        caption             Optional string. The caption of the section.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional string. Specifies an alternate text for an image.
        ---------------     --------------------------------------------------------------------
        position            Optional int. Will position the element in the story list.
        ===============     ====================================================================


        :return: Boolean

        """
        # Create ids
        node_id = "n-" + uuid.uuid4().hex[0:6]

        sections = urlparse(item)

        # Create embed nodes
        self.properties["nodes"][node_id] = {
            "type": "embed",
            "data": {
                "url": item,
                "embedType": "link",
                "title": sections.netloc,
                "description": caption,
                "providerUrl": item,
                "alt": alt_text,
                "display": "card",
            },
        }

        # Add to story children, position counts
        self._add_child(node_id=node_id, position=position)

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

    # ----------------------------------------------------------------------
    def _add_child(self, node_id, position=None):
        # Add to story children, position counts
        root_id = self.properties["root"]
        last = len(self.properties["nodes"][root_id]["children"]) - 1
        if position and position < last:
            self.properties["nodes"][root_id]["children"].insert(node_id)
        else:
            # last node is always credits
            self.properties["nodes"][root_id]["children"].insert(last, node_id)

    # ----------------------------------------------------------------------
    def save(
        self,
        title: Optional[str] = None,
        tags: Optional[list] = None,
        description: Optional[str] = None,
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
        description         Optional string. The description of the StoryMap
        ===============     ====================================================================


        :return: Url of the saved item

        """
        if self._item:
            p = {"text": json.dumps(self._properties)}
            if title:
                p["title"] = title
            if tags:
                p["tags"] = tags
            self._item.update(item_properties=p)
            self._item = self._gis.content.get(self._itemid)
            return self._item.url
        else:
            if title is None:
                title = "Map Journal, %s" % uuid.uuid4().hex[:10]
            if tags is None:
                tags = "Story Map,Map Journal"
            typeKeywords = ",".join(
                [
                    "smstatusdraft",
                    "arcgis-storymaps",
                    "smversiondraft:20.35.0",
                    "smitem1",
                    "Story Map",
                    "Web Map",
                ]
            )
            item = self._gis.content.add(
                item_properties={
                    "title": title,
                    "tags": tags,
                    "text": json.dumps(self._properties),
                    "typeKeywords": typeKeywords,
                    "itemType": "text",
                    "type": "Story Map",
                }
            )
            parse = urlparse(self._gis._con.baseurl)
            isinstance(self._gis, GIS)
            if self._gis._portal.is_arcgisonline:
                url = "%s://%s/apps/StoryMap/index.html?appid=%s" % (
                    parse.scheme,
                    parse.netloc,
                    self._itemid,
                )
            else:
                wa = os.path.dirname(parse.path[1:])
                url = "%s://%s/%s/sharing/rest/apps/StoryMap/index.html?appid=%s" % (
                    parse.scheme,
                    parse.netloc,
                    wa,
                    self._itemid,
                )
            item.update(item_properties={"url": url})
            self._item = self._gis.content.get(self._itemid)
            return self._item.url
