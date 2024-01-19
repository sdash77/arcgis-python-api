from __future__ import annotations
import json
from enum import Enum
from arcgis.auth import EsriSession
from arcgis.auth.tools import LazyLoader
from typing import Union, Any
import requests

arcgis = LazyLoader("arcgis")


class SharingLevel(Enum):
    """
    Sets the sharing level for the `Item`.

    ======================  ========================================================
    **Parameter**            **Description**
    ----------------------  --------------------------------------------------------
    ORG                     Sets the value to have organizational visibility and only
                            authenticated users within the GIS can see/use the item.
    ----------------------  --------------------------------------------------------
    PRIVATE                 Sets the item's sharing level to hidden/private and only
                            the owner of the item can see that item.
    ----------------------  --------------------------------------------------------
    EVERYONE                Make the item public and anyone can use it.
    ======================  ========================================================
    """

    ORG = "ORGANIZATION"
    PRIVATE = "PRIVATE"
    EVERYONE = "EVERYONE"


class SharingGroupManager:
    """
    This class controls the `Group` sharing of a given item.

    ================  ===============================================================
    **Parameter**      **Description**
    ----------------  ---------------------------------------------------------------
    sm                Required SharingManager. The sharing manager reference.
    ================  ===============================================================

    """

    __slots__ = ("_item", "_gis", "_session", "_sm")
    _item: arcgis.gis.Item
    _session: EsriSession
    _gis: arcgis.gis.GIS
    _sm: SharingManager

    # ---------------------------------------------------------------------
    def __init__(self, sm: SharingManager):
        """initializer"""
        self._item = sm._item
        self._gis = sm._gis
        self._session = sm._session
        self._sm = sm

    def __repr__(self) -> str:
        return f"< {self._item.id} SharingGroupManager >"

    def __str__(self) -> str:
        return self.__repr__()

    # ---------------------------------------------------------------------
    def add(self, group: arcgis.gis.Group | str) -> bool:
        """
        Shares a Group with an Item.

        :returns:boolean
        """
        g: str | arcgis.gis.Group | None = None
        g = [grp.id for grp in self.list()]
        do_update = False
        if hasattr(group, "id") and not getattr(group, "id") in g:
            g.append(getattr(group, "id"))
            groups: str = ",".join(g)
            do_update = True
        elif isinstance(group, str) and not group in g:
            g.append(group)
            groups: str = ",".join(g)
            do_update = True
        if do_update:
            self._sm._share(level=self._sm.sharing_level, groups=groups)
            return True
        return False

    # ---------------------------------------------------------------------
    def remove(self, group) -> bool:
        """removes a group that the item is shared with"""
        g: str | arcgis.gis.Group | None = None
        g = [grp.id for grp in self.list()]
        do_update = False
        if hasattr(group, "id"):
            group = getattr(group, "id")
        if isinstance(group, str) and group in g:
            g.pop(g.index(group))
            groups: str = ",".join(g)
            do_update = True
        if do_update:
            self._sm._unshare(groups=group)
            self._sm._share(level=self._sm.sharing_level, groups=groups)
            return True
        return False

    # ---------------------------------------------------------------------
    @property
    def _groups(self) -> list[str]:
        """private method to get the groups shared with a given item."""
        itemid: str = self._item.id
        params: dict[str, Any] = {
            "f": "json",
            "items": itemid,
        }
        url: str = f"{self._gis._portal.resturl}content/itemsgroups"
        resp: requests.Response = self._session.get(url=url, params=params)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        return list(data.keys())

    # ---------------------------------------------------------------------
    def list(self) -> list[arcgis.gis.Group]:
        """
        Lists all the `Group` for the current item

        :returns: list[Group]
        """
        return [arcgis.gis.Group(gis=self._gis, groupid=grp) for grp in self._groups]


class SharingManager:
    """
    Manages a Single Item's Sharing within an organization.

    ================  ===============================================================
    **Parameter**      **Description**
    ----------------  ---------------------------------------------------------------
    item              Required Item. The item to manage the sharing on.
    ----------------  ---------------------------------------------------------------
    gis               Optional GIS. The GIS object to the Item.
    ================  ===============================================================
    """

    __slots__ = ("_item", "_gis", "_session", "_sgm")

    def __init__(
        self,
        item: arcgis.gis.Item,
        *,
        gis: arcgis.gis.GIS | EsriSession | None = None,
    ):
        self._item: arcgis.gis.Item | None = None
        self._gis: arcgis.gis.GIS = None
        self._session: EsriSession | None = None
        self._sgm: SharingGroupManager | None = None

        if isinstance(item, arcgis.gis.Item):
            self._item = item
        else:
            raise ValueError("`item` must be an `Item` object.")
        if isinstance(gis, arcgis.gis.GIS):
            self._session = gis.session
            self._gis = gis
        elif isinstance(gis, EsriSession):
            self._session = gis
            self._gis = item._gis
        elif gis and not isinstance(gis, (EsriSession, arcgis.gis.GIS)):
            raise ValueError("`gis` must be a EsriSession of GIS object.")
        else:
            self._gis = item._gis
            self._session = item._gis.session

    def __repr__(self) -> str:
        return f"< {self._item.id} SharingManager >"

    def __str__(self) -> str:
        return self.__repr__()

    def _share(
        self,
        level: SharingLevel,
        groups: list[arcgis.gis.Group] | str | None = None,
    ) -> dict[str, Any]:
        """
        The share operation shares an item with a public or organization
        sharing level with groups either owned or administered by the user
        performing the request.

        ======================  ========================================================
        **Parameter**            **Description**
        ----------------------  --------------------------------------------------------
        level                   Required SharingLevel. Sets the current state of the item.
        ----------------------  --------------------------------------------------------
        groups                  Optional list[Group]. The individual groups to share
                                with. If the value is set to an empty string, `""` the
                                groups will be unshared.
        ======================  ========================================================
        """
        # if not in org use different url

        if self._gis.users.get(self._item.owner, outside_org=False):
            url: str = "{resturl}content/users/{owner}/shareItems".format(
                resturl=self._gis._portal.resturl, owner=self._item.owner
            )
        else:
            url: str = "{resturl}content/items/{itemid}/share".format(
                resturl=self._gis._portal.resturl, itemid=self._item.itemid
            )

        params: dict[str, Any] = {
            "f": "json",
            "items": self._item.id,
        }
        if level == SharingLevel.ORG:
            params["org"] = True
            params["everyone"] = False
            params["confirmItemControl"] = True
        elif level == SharingLevel.PRIVATE:
            params["org"] = False
            params["everyone"] = False
            params["confirmItemControl"] = True
        elif level == SharingLevel.EVERYONE:
            params["org"] = False
            params["everyone"] = True
            params["confirmItemControl"] = True

        if groups == "" or groups == []:
            params["groups"] = ""
        elif groups is None:
            params["groups"] = ",".join(self.groups._groups)
        elif isinstance(groups, str):
            params["groups"] = groups
        else:
            groups = ""

        params = {
            k: (json.dumps(v) if isinstance(v, bool) else v)
            for (k, v) in params.items()
        }
        resp: requests.Response = self._session.post(url=url, data=params)
        resp.raise_for_status()
        self._item._hydrated = False
        data: dict[str, Any] = resp.json()
        return data

    def _unshare(
        self,
        groups: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """
        The share operation shares an item with a public or organization
        sharing level with groups either owned or administered by the user
        performing the request.

        ======================  ========================================================
        **Parameter**            **Description**
        ----------------------  --------------------------------------------------------
        groups                  Optional list[Group]. The individual groups to share
                                with. If the value is set to an empty string, `""` the
                                groups will be unshared.
        ======================  ========================================================
        """
        # if not in org use different url

        if self._gis.users.get(self._item.owner, outside_org=False):
            url: str = "{resturl}content/users/{owner}/unshareItems".format(
                resturl=self._gis._portal.resturl, owner=self._item.owner
            )
        else:
            url: str = "{resturl}content/items/{itemid}/unshare".format(
                resturl=self._gis._portal.resturl, itemid=self._item.itemid
            )

        params: dict[str, Any] = {
            "f": "json",
            "items": self._item.id,
            "groups": "",
        }

        if groups == "" or groups == []:
            params["groups"] = ""
        elif groups is None:
            return
        elif isinstance(groups, list):
            groups = ",".join(groups)
        params["groups"] = groups
        resp: requests.Response = self._session.post(url=url, data=params)
        resp.raise_for_status()
        self._item._hydrated = False
        data: dict[str, Any] = resp.json()
        return data

    @property
    def groups(self) -> SharingGroupManager:
        """ """
        if self._sgm is None:
            self._sgm = SharingGroupManager(sm=self)
        return self._sgm

    # ----------------------------------------------------------------------
    @property
    def sharing_level(self) -> SharingLevel:
        """
        get/sets the Item's sharing level.


        :returns: SharingLevel
        """
        return self.shared_with["level"]

    # ----------------------------------------------------------------------
    @sharing_level.setter
    def sharing_level(self, value: Union[SharingLevel, str]) -> None:
        """
        get/sets the Item's sharing level.


        :returns: SharingLevel
        """
        if isinstance(value, str):
            for level in SharingLevel:
                name = level.name.lower()
                val = str(level.value).lower()
                if name == value.lower() or val == value.lower():
                    value = level
                    break
        assert isinstance(value, SharingLevel)
        self._share(level=value)
        self._item._hydrated = False
        self._item._hydrate()

    # ----------------------------------------------------------------------
    @property
    def shared_with(self) -> dict[str, Any]:
        """
        The ``shared_with`` property reveals the privacy or sharing status of the current item. An item can be private
        or shared with one or more of the following:
            1. A specified list of groups
            2. All members in the organization
            3. Everyone (including anonymous users).

        :returns: dict[str,Any]

        """
        sw: dict = self._shared_with
        results: dict[str, Any] = {"groups": sw.get("groups", [])}
        if sw["everyone"]:
            results["level"] = SharingLevel.EVERYONE
        elif sw["everyone"] == False and sw["org"]:
            results["level"] = SharingLevel.ORG
        else:
            results["level"] = SharingLevel.PRIVATE
        return results

    # ----------------------------------------------------------------------
    @property
    def _shared_with(self) -> dict[str, Any]:
        """
        The ``shared_with`` property reveals the privacy or sharing status of the current item. An item can be private
        or shared with one or more of the following:
            1. A specified list of groups
            2. All members in the organization
            3. Everyone (including anonymous users).

        .. note::
            If the return is False for `org`, `everyone` and contains an empty list of `groups`, then the
            item is private and visible only to the owner.

        :return:
            A Dictionary in the following format:
            {
            'groups': [],  # one or more Group objects
            'everyone': True | False,
            'org': True | False
            }
        """
        ret_dict: dict[str, Any] = {
            "everyone": False,
            "org": False,
            "groups": [arcgis.gis.Group(self._gis, grp) for grp in self.groups._groups],
        }
        sharing_info: str = self._item.access
        if sharing_info == "public":
            ret_dict["everyone"] = True
            ret_dict["org"] = True

        if sharing_info == "org":
            ret_dict["org"] = True

        return ret_dict
