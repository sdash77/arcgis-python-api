import os
from arcgis._impl.common._isd import InsensitiveDict
from typing import List, Dict, Any
from arcgis._impl.common._deprecate import deprecated


###########################################################################
class NotebookFile:
    """Represents a Single File on the ArcGIS Notebook Server"""

    _da = None
    _definition = None

    # ---------------------------------------------------------------------
    def __init__(self, definition: Dict[str, Any], da: "NotebookDataAccess"):
        self._definition = definition
        self._da = da

    # ---------------------------------------------------------------------
    def __str__(self):
        return f"<NotebookFile file={self.properties.name}>"

    # ---------------------------------------------------------------------
    def __repr__(self):
        return f"<NotebookFile file={self.properties.name}>"

    # ---------------------------------------------------------------------
    @property
    def properties(self):
        """
        returns the properties of the resource

        :return: Dict

        """
        return InsensitiveDict(self._definition)

    # ---------------------------------------------------------------------
    def rename(self, name: str) -> bool:
        """
        Rename the file on the server.

        ===================  ==========================================================================
        **Parameter**         **Description**
        -------------------  --------------------------------------------------------------------------
        name                 Required String. The new name of the file.
        ===================  ==========================================================================

        :return: True if the file was renamed, False or an error if it was not.
        """
        url = f"{self._da._url}/notebookworkspace/move"
        params = {
            "f": "json",
            "source": self.properties.name,
            "target": name,
        }
        return self._da._gis.session.post(url, params).json().get("status") == "success"

    # ---------------------------------------------------------------------
    def download(self) -> str:
        """
        Copies down the data from the server to the local machine

        :return: str as file path
        """
        return self._da._download(filename=self.properties["Name"])

    # ---------------------------------------------------------------------
    @deprecated(deprecated_in="2.4.2", removed_in="2.5.0", current_version="2.4.2")
    def erase(self) -> bool:
        """
        Deletes a file from the system

        :return: Boolean
        """
        return self._da._delete(filename=self.properties["Name"])

    # ---------------------------------------------------------------------
    def delete(self) -> bool:
        """
        Deletes a file from the system. This will permanently delete the file.

        :return: True if the file was deleted, False or an error if it was not.
        """
        return self._da._delete(filename=self.properties["Name"])


###########################################################################
class NotebookDataAccess:
    """
    The Data Access Workspace Directory allows notebook authors to manage files used in their notebooks.
    """

    _url = None
    _gis = None

    # ---------------------------------------------------------------------
    def __init__(self, url, gis):
        self._url = url
        self._gis = gis

    # --------------------------------------------------------------------
    def __repr__(self):
        return "NotebookDataAccess"

    # ---------------------------------------------------------------------
    def __str__(self):
        return "NotebookDataAccess"

    # ---------------------------------------------------------------------
    def upload(self, fp: str) -> bool:
        """
        Uploads a file to the Notebook Server

        ===================  ==========================================================================
        **Parameter**         **Description**
        -------------------  --------------------------------------------------------------------------
        fp                   Required String. The path of the file to upload
        ===================  ==========================================================================

        :return: Boolean
        """

        url = f"{self._url}/notebookworkspace/{os.path.basename(fp)}"
        if os.path.isfile(fp) == False:
            raise ValueError(f"Cannot find file: {fp}")
        additional_headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": f"{os.path.getsize(fp)}",
            "x-ms-blob-type": "BlockBlob",
            "x-ms-version": "2020-02-10",
        }
        resp = self._gis._con.put_raw(
            url, data=open(fp, "rb"), additional_headers=additional_headers
        )
        return resp.status_code >= 200 and resp.status_code < 300

    # ---------------------------------------------------------------------
    @property
    def files(self) -> List[Dict[str, Any]]:
        """
        Lists files that are located in the workspace directory (/arcgis/home) of the user making the request.

        :return: List[Dict[str, Any]]
        """
        if self._gis._is_arcgisonline:
            url = self._url.replace(
                f"/{self._gis.users.me.username}", "/notebooksWorkspace"
            )
        else:
            url = f"{self._url}/notebookworkspace"
        params = {
            "f": "json",
            "restype": "container",
            "comp": "list",
            "token": self._gis._con.token,
        }
        return [
            NotebookFile(f, self)
            for f in self._gis._con.get(url, params).pop("Blobs", [])
        ]

    # ---------------------------------------------------------------------
    def _download(self, filename: str) -> str:
        """
        downloads a file from the
        """
        url = f"{self._url}/notebookworkspace/downloadFile"
        params = {
            "f": "json",
            "fileName": filename,
        }
        return self._gis._con.post(url, params)

    # ---------------------------------------------------------------------
    def _delete(self, filename: str) -> bool:
        """
        downloads a file from the
        """
        url = f"{self._url}/notebookworkspace/deleteFile"
        params = {
            "f": "json",
            "fileName": filename,
        }
        return self._gis._con.post(url, params).get("status") == "success"

    # ---------------------------------------------------------------------
    def create_folder(self, folder: str) -> bool:
        """
        create a folder in your `/arcgis/home` notebook workspace directory.

        ===================  ==========================================================================
        **Parameter**         **Description**
        -------------------  --------------------------------------------------------------------------
        folder               Required String. The name of the folder to create.
        ===================  ==========================================================================

        """
        url = f"{self._url}/notebookworkspace/createFolder"
        params = {
            "f": "json",
            "folderName": folder,
        }
        return self._gis._con.post(url, params).get("status") == "success"
