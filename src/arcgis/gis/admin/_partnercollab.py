from __future__ import annotations
from arcgis.auth import EsriSession
from arcgis.auth.tools import LazyLoader
from typing import Any, Generator
import json
import requests
import urllib.parse
from functools import lru_cache

_arcgis_gis = LazyLoader("arcgis.gis")


@lru_cache(maxsize=255)
def _get_org_id(url: str, session: EsriSession, return_type: str = "url_key") -> str:
    parsed: urllib.parse.ParseResult = urllib.parse.urlparse(url)
    parsed_url: str = f"{parsed.scheme}://{parsed.netloc}/sharing/rest/portals/self"
    params: dict[str, Any] = {
        "f": "json",
    }
    resp: requests.Response = session.get(url=parsed_url, params=params)
    resp.raise_for_status()
    if return_type == "url_key":
        return resp.json().get("urlKey")
    else:
        return resp.json().get("id")


class PartneredCollaboration:
    """Represents a single partnered collaboration for the organization."""

    _url: str
    _gis: _arcgis_gis.GIS
    _session: EsriSession
    _properties: dict[str, Any] | None = None

    def __init__(self, url: str, gis: _arcgis_gis.GIS) -> None:
        self._gis: _arcgis_gis.GIS = gis
        self._url: str = url
        self._session = gis.session

    @property
    def url(self) -> str:
        return self._url

    @property
    def session(self) -> EsriSession:
        return self._session

    @property
    def properties(self) -> dict[str, Any]:
        if self._properties is None:
            url: str = f"{self.url}"
            params: dict[str, Any] = {
                "f": "json",
            }
            resp: requests.Response = self.session.get(url=url, params=params)
            resp.raise_for_status()
            self._properties = resp.json()
        return self._properties

    @property
    def suspend(self) -> bool:
        """
        Gets/sets the status of the collaboration.  To suspend collaboration, set the value to false.

        :returns: Bool, where False means the collaboration is not suspended, and True means the relationship is suspended.
        """
        return self.properties["to"]["state"] == "suspended"

    @suspend.setter
    def suspend(self, value: bool) -> None:
        state = self.properties["to"]["state"] == "suspended"
        if state == value:
            return
        else:
            if value == False:
                state = "active"
            elif value == True:
                state = "suspended"
            url: str = f"{self.url}/update"
            orgid: str = self.properties["to"]["orgId"]
            params: dict[str, Any] = {
                "f": "json",
                "orgId": orgid,
                "state": state,
            }
            self.session.post(url=url, data=params)
            self._properties = None

    @property
    def groups(self) -> Generator[_arcgis_gis.Group]:
        """Returns the groups associated with the Partnered Collaboration"""
        to_id: str = self.properties["to"]["orgId"]
        from_id: str = self.properties["from"]["orgId"]
        for group in self._gis.groups.search(f"orgid:{from_id} memberorgids:{to_id}"):
            yield group

    @property
    def search_users(self) -> bool:
        """Enables/Disable Searching for users on the partnered collaboration"""
        return self.properties["to"]["usersAccess"]

    @search_users.setter
    def search_users(self, value: bool) -> None:
        """Enables/Disable Searching for users on the partnered collaboration"""
        if self.properties["to"]["usersAccess"] == value:
            return
        if self.properties["to"]["established"] == -1:
            raise ValueError(
                "You cannot change the `search_users` until the collaboration is accepted."
            )
        url: str = f"{self.url}/update"
        orgid: str = self.properties["to"]["orgId"]
        params: dict[str, Any] = {
            "f": "json",
            "orgId": orgid,
            "searchUsers": json.dumps(value),
        }
        self.session.post(url=url, data=params)
        self._properties = None

    def delete(self, message: str | None = None) -> bool:
        """This operation ends the partnered collaboration"""
        url: str = f"{self.url}/delete"
        params: dict[str, Any] = {
            "f": "json",
            "message": message,
            "async": json.dumps(True),
        }
        resp: requests.Response = self.session.post(url=url, data=params)
        resp.raise_for_status()
        return resp.json().get("success", False)


class PartneredCollabManager:
    """
    Your ArcGIS Online organization can use partnered collaborations to
    share content with other ArcGIS Online organizations. When two or more
    organizations create a partnered collaboration, they enter a
    partnership that allows their members to work closely with each other
    and each other's content using groups.

    For instance, wildlife management departments of two adjacent cities,
    each with their own ArcGIS Online organization, may want to share their
    wildlife maps and layers with each other. These maps and layers will be
    used by both cities to better monitor the movement of wildlife between
    them. To do this, both city organizations can create a partnered
    collaboration through which members can share content. Each
    organization continues to own and manage its own content while
    allowing the other to view and contribute. Once you have established a
    partnered collaboration with another organization, you create and use
    groups to share content with members of collaborating organizations.


    """

    _url: str
    _gis: _arcgis_gis.GIS
    _session: EsriSession
    _properties: dict[str, Any] | None = None

    def __init__(self, url: str, gis: _arcgis_gis.GIS) -> None:
        if gis._is_arcgisonline == False:
            raise ValueError("The `GIS` must be an ArcGIS Online Organization")
        url = url.split("/sharing/rest")[0] + "/sharing/rest/portals/self/trustedOrgs"
        self._gis: _arcgis_gis.GIS = gis

        self._url: str = url
        self._session = gis.session

    @property
    def url(self) -> str:
        """returns the URL of the endpoint"""
        return self._url

    @property
    def session(self) -> EsriSession:
        """returns the current EsriSession"""
        return self._session

    @property
    def properties(self) -> dict[str, Any]:
        """
        Returns the partnered properties
        :return: dict
        """
        if self._properties is None:
            url: str = f"{self.url}"
            params: dict[str, Any] = {
                "f": "json",
            }
            resp: requests.Response = self.session.get(url=url, params=params)
            resp.raise_for_status()
            self._properties = resp.json()
        return self._properties

    @property
    def limits(self) -> dict[str, Any]:
        """Returns the Organization's limits of creating collaborations"""
        url: str = f"{self.url.replace('/trustedOrgs', '')}/limits"
        params: dict[str, Any] = {
            "f": "json",
            "limitsType": "Collaboration",
            "limitName": "MaxTrustedOrgs",
        }
        resp: requests.Response = self.session.get(url=url, params=params)
        resp.raise_for_status()
        return resp.json()

    def collaborations(
        self, include_hub: bool = False
    ) -> Generator[PartneredCollaboration]:
        """Returns all the partnered collaboration for the current organization"""
        url: str = f"{self.url}"
        params = {
            "f": "json",
            "num": 100,
            "start": 1,
        }
        resp: requests.Response = self.session.get(url=url, params=params)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        for org in data["trustedOrgs"]:
            orgid: str = org["to"]["orgId"]
            if include_hub:
                yield PartneredCollaboration(url=f"{url}/{orgid}", gis=self._gis)
            elif include_hub == False and org["from"]["hub"] == False:
                yield PartneredCollaboration(url=f"{url}/{orgid}", gis=self._gis)
        while data.get("nextStart", -1) != -1:
            resp: requests.Response = self.session.get(url=url, params=params)
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
            for org in data["trustedOrgs"]:
                orgid: str = org["to"]["orgId"]
                if include_hub:
                    yield PartneredCollaboration(url=f"{url}/{orgid}", gis=self._gis)
                elif include_hub == False and org["from"]["hub"] == False:
                    yield PartneredCollaboration(url=f"{url}/{orgid}", gis=self._gis)

    # ---------------------------------------------------------------------
    @property
    def coordinators(self) -> Generator[_arcgis_gis.User]:
        """returns the coordinators for partner collaborations"""
        params: dict[str, Any] = {
            "f": "json",
            "num": 100,
            "collaborators": "false",
            "type": "collaboration",
            "start": 1,
        }
        url: str = self.url.replace("/trustedOrgs", "/contacts")
        resp: requests.Response = self.session.get(url=url, params=params)
        data: dict = resp.json()
        for user in data.get("users", []):
            yield _arcgis_gis.User(gis=self._gis, username=user["username"])
        while data.get("nextStart", -1) > -1:
            params["start"] = data.get("nextStart", -1)
            url: str = self.url.replace("/trustedOrgs", "/contacts")
            resp: requests.Response = self.session.get(url=url, params=params)
            data: dict = resp.json()
            for user in data.get("users", []):
                yield _arcgis_gis.User(gis=self._gis, username=user["username"])

    # ---------------------------------------------------------------------
    @coordinators.setter
    def coordinators(self, value: list[_arcgis_gis.User]) -> None:
        if value is None:
            value = []
        users: list[str] = [user.username for user in value]
        params: dict[str, Any] = {
            "f": "json",
            "users": ",".join(users),
            "type": "collaboration",
        }

        url: str = f"{self.url.replace('/trustedOrgs', '/updateContacts')}"
        resp: requests.Response = self.session.post(url=url, data=params)
        resp.raise_for_status()
        data: dict = resp.json()
        if not "success" in data:
            raise Exception(f"{data}")

    # ---------------------------------------------------------------------
    def create(
        self,
        message: str,
        org_url: str | None = None,
        org_id: str | None = None,
        search_users: bool = False,
    ) -> bool:
        """Creates a partnered collaboration on the ArcGIS Online site.

        ================  ===============================================================
        **Parameter**      **Description**
        ----------------  ---------------------------------------------------------------
        message           Required String. The message to send to the organization about
        ----------------  ---------------------------------------------------------------
        org_url           Required String. The url of the organization to partner with.
        ----------------  ---------------------------------------------------------------
        org_id            Required String. The ID of the organization to partner with.
        ----------------  ---------------------------------------------------------------
        search_users      Optional boolean. Allows the partnered organization to search for users.
        ================  ===============================================================

        :return: bool
        """
        if org_id is None and org_url is None:
            raise ValueError(
                "Please provide a `url_id` or `org_url` to `add` a new partnered collaboration."
            )
        url_key: str = _get_org_id(url=org_url, session=EsriSession())
        url: str = f"{self.url.replace('/trustedOrgs', '')}/addTrustedOrg"
        params: dict[str, Any] = {
            "orgId": org_id,
            "urlKey": url_key,
            "message": message,
            "searchUsers": json.dumps(search_users),
            "f": "json",
        }
        if params["orgId"] is None:
            del params["orgId"]
        if params["urlKey"] is None:
            del params["urlKey"]
        resp: requests.Response = self.session.post(url=url, data=params)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        if data.get("success", False):
            return True
        else:
            return data
