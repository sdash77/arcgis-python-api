from __future__ import annotations
from typing import Optional, Union
import uuid
from enum import Enum
from arcgis.auth.tools import LazyLoader
import copy
from ._ref import templates

arcgis = LazyLoader("arcgis")
json = LazyLoader("json")
time = LazyLoader("time")


class Templates(Enum):
    BLANKFULLSCREEN = "blank fullscreen"
    BLANKSCROLLING = "blank scrolling"
    FOLDABLE = "foldable"
    LAUNCHPAD = "launchpad"
    JEWELERYBOX = "jewelrybox"
    BILLBOARD = "billboard"
    JOURNEY = "journey"
    RIBBON = "ribbon"
    GENERAL = "general"
    INTRODUCTION = "introduction"
    GALLERY = "gallery"
    EPIC = "epic"
    SNAPSHOT = "snapshot"
    SUMMARY = "summary"
    TIMELINE = "timeline"
    SCENIC = "scenic"
    EXHIBITION = "exhibition"
    DART = "dart"
    POCKET = "pocket"
    QUICKNAVIGATION = "quick navigation"
    PARALLAX = "parallax"
    DASH = "dash"
    INDICATOR = "indicator"
    MONITOR = "monitor"
    REVEAL = "reveal"

    def preview(self, width: Optional[int] = 800, height: Optional[int] = 500):
        import threading
        import time

        def thread_delete(item):
            time.sleep(3)
            item.delete()

        try:
            temp = WebExperience(template=self.value)
            temp._item.share(everyone=True)
            temp.publish()
            from IPython.display import IFrame

            frame = IFrame(
                src=temp._item.url,
                width=width,
                height=height,
            )
            delete = threading.Thread(target=thread_delete, args=([temp._item]))
            delete.start()
            return frame

        except:
            return False


class WebExperience(object):

    """
    A Web Experience is web-based application that provides viewers with an interactive
    interface to maps, data, feature layers, and other components of the creator's design.
    Though these experiences are normally constructed via a GUI found on ArcGIS Online or
    Enterprise, this class provides users a host of supplemental options to manage experiences,
    in addition to basic creation of experiences.

    ===============     ====================================================================
    **Argument**        **Description**
    ---------------     --------------------------------------------------------------------
    item                Optional String or Item. The string for an item id or an item of type
                        'Web Experience'. If no item is passed, a new experience is created
                        and saved to your active portal.
    ---------------     --------------------------------------------------------------------
    gis                 Optional instance of :class:`~arcgis.gis.GIS`. If none provided the active gis is used.
    ---------------     --------------------------------------------------------------------
    template            Optional string. If a new experience is being created, the template
                        used to construct the layout. If necessary and none provided, template
                        will default to `blank fullscreen`.
    ---------------     --------------------------------------------------------------------
    name                Optional string. If a new experience is being created, the name of the
                        item. Otherwise, will default to "Experience via Python" followed by a
                        random number.
    ===============     ====================================================================
    """

    _properties = None
    _gis = None
    _itemid = None
    _item = None
    _resources = None
    _expdict = {}
    _draft = {}

    def __init__(
        self,
        item: Optional[Union[arcgis.gis.Item, str]] = None,
        gis: Optional[arcgis.gis.GIS] = None,
        template: Optional[Union[Templates, str]] = None,
        name: Optional[str] = None,
    ):
        if gis is None:
            gis = arcgis.env.active_gis
            self._gis = gis
        else:
            self._gis = gis
        if gis is None or gis._portal.is_logged_in is False:
            # check to see if user is authenticated
            raise Exception("Must be logged into a Portal Account")
        if item and isinstance(item, str):
            # get item using the item id
            item = gis.content.get(item)
        if item and isinstance(item, arcgis.gis.Item) and item.type == "Web Experience":
            # set item properties
            self._item = item
            self._itemid = self._item.itemid
            self._resources = self._item.resources.list()
            self._expdict = self._item.resources.get("config/config.json")
            self._draft = self._item.resources.get("config/config.json")
            self._gis = self._item._gis
        elif (
            item and isinstance(item, arcgis.gis.Item) and item.type != "Web Experience"
        ):
            # Throw error if item is not of type Story Map
            raise ValueError("Item is not a Web Experience")
        else:
            self._create_new_experience(template=template, name=name)

    # -----------------------------------------------------------------------------------
    def _create_new_experience(self, template="blank fullscreen", name=None):
        """
        If no experience is specified when creating a WebExperience, this helper function
        creates a new experience and saves it as an item to the active GIS. Users can specify
        a template from the experience builder to create their template, in addition to a custom
        item name (done as arguments in the initial creation of the WebExperience).
        """

        if isinstance(template, Templates):
            template = template.value

        # retrieve template for experience
        if template is None:
            template = "blank fullscreen"

        temp_low = template.lower()
        if temp_low in arcgis.apps.expbuilder._ref.templates:
            temp_dict = copy.deepcopy(arcgis.apps.expbuilder._ref.templates[temp_low])
        else:
            temp_dict = copy.deepcopy(
                arcgis.apps.expbuilder._ref.templates["blank fullscreen"]
            )

        temp_dict["attributes"]["portalUrl"] = self._gis.url
        # temp_dict["timestamp"]
        # create item and generate basic properties
        if name is None:
            title = "Experience via Python %s" % uuid.uuid4().hex[:10]
        else:
            title = name
        keywords = ",".join(
            [
                "EXB Experience",
                "JavaScript",
                "Ready To Use",
                "status: Draft",
                "Web Application",
                "Web Experience",
                "Web Page",
                "Web Site",
                "expbuilderapp:python-api-" + arcgis.__version__,
            ]
        )
        item_properties = {
            "type": "Web Experience",
            "title": title,
            "typeKeywords": keywords,
        }

        # add to active gis and set properties
        item = self._gis.content.add(item_properties=item_properties)

        # assign to experience properties
        self._item = item
        self._itemid = item.itemid
        self._item.resources.add(
            folder_name="config", file_name="config.json", text=temp_dict
        )
        self._resources = self._item.resources.list()
        self._expdict = temp_dict
        self._draft = temp_dict

    # ----------------------------------------------------------------------
    def save(
        self,
        title: Optional[str] = None,
        tags: Optional[list] = None,
        access: str = None,
        publish: bool = False,
    ):
        """
        This method will save your Web Experience to your active GIS. The experience will be saved
        with unpublished changes unless the `publish` parameter is set to True. Note that this is
        different from the `publish()` method in that this will save and publish the unsaved draft
        of the WebExperience object, as opposed to the already existing save state.

        The title only needs to be specified if a change is wanted, otherwise the existing title
        is used.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Optional string. The new title of the WebExperience, if desired.
        ---------------     --------------------------------------------------------------------
        tags                Optional string. Updated tags for the WebExperience, if desired.
        ---------------     --------------------------------------------------------------------
        access              Optional string. The sharing setting of the WebExperience. If none
                            is specified, the current access is kept. This is used when the
                            `publish` parameter is set to True.

                            Values: `private` | `org` | `public`
        ---------------     --------------------------------------------------------------------
        publish             Optional boolean. If True, the experience is saved and also
                            published. Default is False, meaning the experience is saved with
                            unpublished changes.
        ===============     ====================================================================


        :return: A boolean indicating the success of the operation.
        """

        keywords = self._item.typeKeywords
        for i in range(len(keywords)):
            if keywords[i] == "status: Published":
                keywords[i] = "status: Changed"
        item_properties = {}
        if title:
            item_properties["title"] = title
        if tags:
            item_properties["tags"] = tags

        self._expdict = self._draft
        self._item.resources.update(
            folder_name="config", file_name="config.json", text=self._expdict
        )
        self._resources = self._item.resources.list()
        if publish:
            for i in range(len(keywords)):
                if "status" in keywords[i]:
                    keywords[i] = "status: Published"
            if access:
                item_properties["access"] = access
            item_properties["typeKeywords"] = keywords
            if self._gis._is_agol:
                url = "https://experience.arcgis.com/experience/" + self._item.itemid
            else:
                url = (
                    self._gis.url
                    + "/apps/experiencebuilder/experience/?id="
                    + self._item.itemid
                )
            item_properties["url"] = url
            return self._item.update(
                item_properties=item_properties, data=self._expdict
            )
            # self.publish(item_properties = item_properties, data = self._expdict)
        else:
            item_properties["typeKeywords"] = keywords
            return self._item.update(item_properties=item_properties)

    # ----------------------------------------------------------------------
    def reset(self):
        """
        Resets any changes that the user has made to the last saved state. Note that
        this only applies to changes made through a Python API object, and not the GUI.

        :return: A boolean indicating the success of the operation.
        """

        self._draft = self._expdict
        return self._item.resources.update(
            folder_name="config", file_name="config.json", text=self._expdict
        )

    # ----------------------------------------------------------------------
    def view(self, width: Optional[int] = 800, height: Optional[int] = 500):
        """
        Shows the currently published experience, if possible. Default width is 800 and default
        height is 500. Note that this displays the actively published version of the
        WebExperience object; to visualize unsaved changes, `preview()` should be used.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        width               Optional integer. The desired width to show the preview.
        ---------------     --------------------------------------------------------------------
        height              Optional integer. The desired height to show the preview.
        ===============     ====================================================================

        :return:
            An IFrame display of the story map if possible, else the item url is returned to be
            clicked on. If the item is unpublished, the function returns False.
        """
        keywords = self._item.typeKeywords
        if "status: Published" in keywords:
            from IPython.display import IFrame

            try:
                frame = IFrame(
                    src=self._item.url,
                    width=width,
                    height=height,
                )
                return frame
            except:
                return self._item.url
        else:
            return False

    # ----------------------------------------------------------------------
    def delete(self):
        """
        Deletes the experience and its associated item from the portal.

        :return:
            A boolean indicating the success of the operation.
        """
        item = self._gis.content.get(self._itemid)
        return item.delete()

    # ----------------------------------------------------------------------
    def _add_resource(self, file=None, resource_name=None, text=None, access="inherit"):
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
        properties = {
            "editInfo": {
                "editor": self._gis._username,
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

        self._resources = self._item.resources.list()
        return resp

    # ----------------------------------------------------------------------
    def duplicate(
        self,
        title: Optional[str] = None,
        tags: Optional[Union[list[str], str]] = None,
        include_private: Optional[bool] = None,
    ):
        """
        Creates a copy of the experience within the active GIS. Returns a new
        WebExperience object that retains the unsaved changes from the original.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Optional string. The name of the new experience. If left blank, the
                            new item copies the name of the original.
        ---------------     --------------------------------------------------------------------
        tags                Optional string. The desired tags for the new item, separated by
                            commas.
        ---------------     --------------------------------------------------------------------
        include_private     Optional boolean. If True, the private resources of the original
                            item will be included in the new item.
        ===============     ====================================================================

        :return:
            The newly created WebExperience object.

        """
        new_item = self._item.copy_item(
            title=title,
            tags=tags,
            include_resources=True,
            include_private=include_private,
        )
        if new_item:
            new_exp = WebExperience(new_item)
            new_exp._draft = self._draft
            return new_exp
        else:
            return False

    # ----------------------------------------------------------------------
    def publish(self, access: str = None):
        """
        Publishes the last saved version of the experience. Leaves unsaved changes intact,
        but doesn't publish them. Also allows user to set access level of published experience.
        Note that if a user wishes to publish the draft version of the WebExperience they're
        working on, they should do that through the `save()` method.

        :return:
            A boolean indicating the success of the operation.
        """
        keywords = self._item.typeKeywords
        item_properties = {}
        for i in range(len(keywords)):
            if "status" in keywords[i]:
                keywords[i] = "status: Published"
        if access:
            item_properties["access"] = access
        item_properties["typeKeywords"] = keywords
        if self._gis._is_agol:
            url = "https://experience.arcgis.com/experience/" + self._item.itemid
        else:
            url = (
                self._gis.url
                + "/apps/experiencebuilder/experience/?id="
                + self._item.itemid
            )
        item_properties["url"] = url
        return self._item.update(item_properties=item_properties, data=self._expdict)

    # ----------------------------------------------------------------------
    def preview(self, width: Optional[int] = 800, height: Optional[int] = 500):
        """
        Show a preview of the current experience draft. The default is a width of 800 and height of 500.
        Note that this should be used to visualize unsaved changes to the WebExperience object; to see
        the actively published version of the object, `view()` should be used.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        width               Optional integer. The desired width to show the preview.
        ---------------     --------------------------------------------------------------------
        height              Optional integer. The desired height to show the preview.
        ===============     ====================================================================

        :return:
            An IFrame display of the story map if possible, else the item url is returned to be
            clicked on.
        """
        import threading
        import time

        def thread_delete(item):
            time.sleep(3)
            item.delete()

        try:
            dummy_exp = self.duplicate()
            dummy_exp._item.share(everyone=True)
            dummy_exp.save(publish=True)
            from IPython.display import IFrame

            frame = IFrame(
                src=dummy_exp._item.url,
                width=width,
                height=height,
            )
            delete = threading.Thread(target=thread_delete, args=([dummy_exp._item]))
            delete.start()
            return frame

        except:
            return self._item.url

    # ----------------------------------------------------------------------
    def clone(self, target, owner, **kwargs):
        """
        Clones the experience and all of it's data sources to a target GIS. User must
        have admin privileges on the original item's GIS, and provide an authenticated
        instance of a target GIS. Users must also specify the name of an account on the
        target GIS to own the items. Also accepts arguments for :class:`~arcgis.gis.Item.clone_items()`

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        target              Required GIS. An authenticated instance of the GIS that the user
                            wishes to clone the experience to.
        ---------------     --------------------------------------------------------------------
        owner               Required string. The username of the account that will be the owner
                            of the experience and its data source items in the target GIS.
        ---------------     --------------------------------------------------------------------
        **kwargs            Optional additional arguments. See ``Item.clone_items()`` for the full
                            list.
        ===============     ====================================================================

        :return:
            The item corresponding to the cloned experience in the target GIS.
        """

        def _clone_dict(data_dict, source, target, owner, **kwargs):
            """
            Helper function to clone items and update appropriate dict
            """
            new_dict = data_dict
            new_dict["attributes"]["portalUrl"] = target.url
            for k, v in new_dict["dataSources"].items():
                v["portalUrl"] = target.url
                item = source.content.get(v["itemId"])
                clone_result = target.content.clone_items([item], owner=owner, **kwargs)
                if clone_result:
                    v["itemId"] = clone_result[0].itemid
                else:
                    targ_item = target.content.search(item.title)[0]
                    v["itemId"] = targ_item.itemid

            return new_dict

        exp_clone = target.content.clone_items([self._item], owner=owner, **kwargs)
        if exp_clone:
            new_dict = _clone_dict(self._expdict, self._gis, target, owner, **kwargs)
            target_exp = WebExperience(exp_clone[0])
            target_exp._expdict = new_dict
            target_exp._item.resources.update(
                folder_name="config", file_name="config.json", text=target_exp._expdict
            )
            keywords = target_exp._item.typeKeywords
            for word in keywords:
                if "status" in word:
                    if "Published" in word or "Changed" in word:
                        new_data = _clone_dict(
                            self._item.get_data(), self._gis, target, owner, **kwargs
                        )
                        target_exp._item.update(item_properties={}, data=new_data)
                    else:
                        target_exp._item.update(
                            item_properties={}, data={"__not_publish": True}
                        )
                    break
            return target_exp._item
        else:
            return False
