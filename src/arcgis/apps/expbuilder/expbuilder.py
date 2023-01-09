from __future__ import annotations
import os
from typing import Optional, Union
import uuid
from enum import Enum
from arcgis.auth.tools import LazyLoader
import re
import copy
import json
from ._ref import templates

arcgis = LazyLoader("arcgis")
json = LazyLoader("json")
time = LazyLoader("time")


class WebExperience(object):

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
        template: Optional[str] = None,
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
    def reset_save(self):
        self._draft = self._expdict
        return self._item.resources.update(
            folder_name="config", file_name="config.json", text=self._expdict
        )

    # ----------------------------------------------------------------------
    def preview_changes(self):
        return self._item.resources.update(
            folder_name="config", file_name="config.json", text=self._draft
        )

    # ----------------------------------------------------------------------
    def delete_experience(self):
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
        tags: Optional[str] = None,
        include_private: Optional[bool] = None,
    ):
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
    def publish(self):

        draft = self._item.resources.get("config/config.json")
        self._item.update(data=draft)

    # ----------------------------------------------------------------------
    def show(self, width: Optional[int] = 800, height: Optional[int] = 500):
        """
        Show a preview of the experience. The default is a width of 800 and height of 500.

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
        Clones the experience to a target GIS. User must specify
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
