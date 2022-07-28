from arcgis.gis import GIS
from typing import TypeVar

T = TypeVar("T")
V = TypeVar("V")


class Container:
    """
    Represents a Single Notebook Container

    ================  ===============================================================================
    **Argument**      **Description**
    ----------------  -------------------------------------------------------------------------------
    url               Required String. The url for the container.
    ----------------  -------------------------------------------------------------------------------
    gis               Required GIS. The ArcGIS Online connection object.
    ================  ===============================================================================


    """

    _properties = None

    def __init__(self, url: str, gis: GIS):
        """initalizer"""
        self._url = url
        self._gis = gis

    @property
    def properties(self):
        if self._properties is None:
            url = f"{self._url}"
            params = {"f": "json"}
            self._properties = self._gis._con.get(url, params)
        return self._properties

    def terminate(self) -> bool:
        """stops the current container"""
        url = f"{self._url}/terminateContainer"
        params = {"f": "json"}
        return self._gis._con.get(url, params)

    def notebooks(self) -> list[dict[T, V]]:
        """returns a list of notebooks running in the current container"""
        url = f"{self._url}/notebooks"
        params = {"f": "json"}
        return self._gis._con.get(url, params)

    def close(self, notebook_id: str) -> bool:
        """closes a notebook"""
        url = f"{self._url}/notebooks/{notebook_id}/closeNotebook"
        params = {"f": "json"}
        return self._gis._con.post(url, params)


class ContainerManagement:
    """
    ================  ===============================================================================
    **Argument**      **Description**
    ----------------  -------------------------------------------------------------------------------
    url               Required String. The base url for the ContainerManagement endpoints.
    ----------------  -------------------------------------------------------------------------------
    gis               Required GIS. The ArcGIS Online connection object.
    ================  ===============================================================================

    """

    def __init__(self, url: str, gis: GIS):
        self._url = url
        self._gis = gis

    def lists(self) -> list[dict[T, V]]:
        """Returns a list of containers"""
        url = "{self._url}"
        params = {"f": "json"}
        return self._gis._con.get(url, params)

    def get(self, id: str) -> Container:
        """Gets an instance of a container"""
        return Container(url=f"{self._url}/{id}", gis=self._gis)

    def start(self, runtime: str, instance_type: str) -> bool:
        """starts a container"""
        url = "{self._url}/startContainer"
        params = {
            "f": "json",
            "notebookRuntimeId": runtime,
            "instanceTypeName": instance_type,
        }
        res = self._gis._con.post(url, params)
        return res.get("success", False)
