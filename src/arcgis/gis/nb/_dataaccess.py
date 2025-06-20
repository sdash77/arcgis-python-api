import os
from arcgis._impl.common._isd import InsensitiveDict
from typing import List, Dict, Any
from arcgis._impl.common._deprecate import deprecated
from arcgis.gis import User

def _rename(
    da: "NotebookDataAccess", folder_name: str, new_name: str
) -> bool:
    """
    Renames a folder in the notebook workspace.

    :param da: NotebookDataAccess instance.
    :param folder_name: The current name of the folder to rename.
    :param new_name: The new name for the folder.
    :return: True if the folder was renamed successfully, False otherwise.
    """
    if da._gis._is_agol:
        url = f"{da._url}/move".replace("/azureblob/", f"/{da._username}/")
    else:
        url = f"{da._url}/{da._username}/notebookworkspace/move"
    params = {
        "f": "json",
        "source": folder_name,
        "target": new_name,
        "targetUserName": da._username,
        "token": da._gis._con.token,
    }
    return da._gis.session.post(url, params).json().get("status") == "success"

def _get_folders(da: "NotebookDataAccess", folder_name: str | None) -> List["NotebookFolder"]:
    if da._gis._is_agol:
        url = f"{da._url}/notebooksWorkspace"
    else:
        url = f"{da._url}/notebookworkspace"
    params = {
        "f": "json",
        "restype": "container",
        "comp": "list",
        "delimiter": "/",
        "token": da._gis._con.token,
    }
    if folder_name:
        params["prefix"] = folder_name
    response = da._gis._con.get(url, params)
    # When creating subfolders the name should always have the folder to which it belongs as the prefix
    folders = [
        NotebookFolder(f["Name"], da)
        for f in response.get("Blobs", [])
        if f["Properties"].get("ResourceType").lower() == "directory"
    ]
    
    # Include root folder only if folder_name is None
    if folder_name is None:
        folders.insert(0, NotebookFolder("", da))
    return folders

def _create_folder(
    da: "NotebookDataAccess", folder_path: str, folder_name: str
) -> bool:
    """
    Creates a folder in the notebook workspace.

    :param da: NotebookDataAccess instance.
    :param folder_name: The name of the folder to create.
    :return: True if the folder was created successfully, False otherwise.
    """
    if da._gis._is_agol:
        url = f"{da._url}/{da._username}/createFolder".replace(
            "/azureblob", ""
        )
    else:
        url = f"{da._url}/notebookworkspace/createFolder"
    params = {
        "f": "json",
        "folderName": f"{folder_path}{folder_name}",
        "token": da._gis._con.token,
    }
    result = da._gis._con.post(url, params)
    if result.get("status") == "success":
        return NotebookFolder(f"{folder_path}{folder_name}/", da)  
    
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
        return f"<NotebookFile file={self.name}>"

    # ---------------------------------------------------------------------
    def __repr__(self):
        return f"<NotebookFile file={self.name}>"

    # ---------------------------------------------------------------------
    @property
    def name(self) -> str:
        """
        Get the file name

        :return: str - The name of the file.
        """
        return self._definition.get("Name").strip("/").split("/")[-1]

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
        return _rename(
            da=self._da,
            folder_name=self.properties["Name"],
            new_name=name,
        )

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
        return self.delete()

    # ---------------------------------------------------------------------
    def delete(self) -> bool:
        """
        Deletes a file from the system. This will permanently delete the file and the action cannot be undone.

        :return: True if the file was deleted, False or an error if it was not.
        """
        return self._da._delete(filename=self.properties["Name"])


###########################################################################
class NotebookFolder:
    """
    Represents a folder in the ArcGIS Notebook Server workspace.
    This class allows you to manage files and subfolders within a specific folder in the notebook workspace directory.
    """

    _da = None
    _folder_name = None
    _files = None

    # ---------------------------------------------------------------------
    def __init__(self, folder_name: str, da: "NotebookDataAccess"):
        self._folder_name = folder_name
        self._da = da
        self._url = da._url
        self._is_agol = da._gis._is_arcgisonline

    # ---------------------------------------------------------------------
    def __str__(self):
        return f"<NotebookFolder: {self.name}>"

    # ---------------------------------------------------------------------
    def __repr__(self):
        return f"<NotebookFolder: {self.name}>"

    # ---------------------------------------------------------------------
    @property
    def name(self) -> str:
        """
        Get or set the name of the folder.

        ====================    ==========================================================================
        **Parameter**           **Description**
        --------------------    --------------------------------------------------------------------------
        new_name                Required String. The name of the folder. This will rename the folder.
        ====================    ==========================================================================

        :return: str - The name of the folder.
        """
        return self._folder_name.strip("/").split("/")[-1] or "Home"

    # ---------------------------------------------------------------------
    def rename(self, name: str) -> bool:
        """
        Rename the folder.
        
        ===================  ==========================================================================
        **Parameter**         **Description**
        -------------------  --------------------------------------------------------------------------
        name                 Required String. The new name of the folder.
                             The name must be a simple, non-empty name without slashes.
        ===================  ==========================================================================
        
        :return: True if the folder was renamed, False or an error if it was not.
        """
        if self.name == "Home":
            raise ValueError("Cannot rename the root folder 'Home'. Please create a subfolder instead.")
        if not isinstance(name, str):
            raise ValueError("Folder name must be a string.")
        if "/" in name or name.strip() == "":
            raise ValueError(
                "Folder name must be a simple, non-empty name without slashes."
            )
        current_name = self._folder_name
        parts = self._folder_name.strip("/").split("/")
        parts[-1] = name
        self._folder_name = "/".join(parts) + "/"

        return _rename(
            da=self._da,
            folder_name=current_name,
            new_name=self._folder_name,
        )

    # ---------------------------------------------------------------------
    @property
    def folders(self) -> List["NotebookFolder"]:
        """
        Returns the subfolders in the folder.

        :return: List[NotebookFolder] - A list of NotebookFolder objects representing the subfolders.
        """
        return _get_folders(
            da=self._da,
            folder_name=self._folder_name,
        )

    # ---------------------------------------------------------------------
    @property
    def files(self) -> List[NotebookFile]:
        """
        Returns the files in the folder.

        :return: List[NotebookFile] - A list of NotebookFile objects representing the files in the folder.
        """
        if self._is_agol:
            url = f"{self._url}/notebooksWorkspace"
        else:
            url = f"{self._url}/notebookworkspace"
        params = {
            "f": "json",
            "restype": "container",
            "comp": "list",
            "prefix": self._folder_name,
            "token": self._da._gis._con.token,
        }
        response = self._da._gis._con.get(url, params)
        return [NotebookFile(f, self._da) for f in response.get("Blobs", [])]

    # ---------------------------------------------------------------------
    def create_folder(self, folder_name: str) -> bool:
        """
        Create a subfolder in the current folder.

        ===================  ==========================================================================
        **Parameter**         **Description**
        -------------------  --------------------------------------------------------------------------
        folder_name          Required String. The name of the subfolder to create.
                             This will create a subfolder within the current folder.
        ===================  ==========================================================================

        :return: True if the folder was created, False or an error if it was not.
        """
        return _create_folder(
            da=self._da,
            folder_path=self._folder_name,
            folder_name=folder_name,
        )

    # ---------------------------------------------------------------------
    def _resolve_files(self, fp):
        if isinstance(fp, list):
            return [f for f in fp if os.path.isfile(f)]

        if os.path.isdir(fp):
            # If the path is a directory, get all files in the directory
            return [
                os.path.join(fp, f)
                for f in os.listdir(fp)
                if os.path.isfile(os.path.join(fp, f))
            ]

        if os.path.isfile(fp):
            # If the path is a file, return it as a list
            return [fp]

        raise ValueError(
            f"Invalid file path: {fp}. It must be a file or a directory containing files."
        )

    # ---------------------------------------------------------------------
    def _upload_single_file(self, file_path: str) -> bool:
        if not os.path.isfile(file_path):
            raise ValueError(f"File {file_path} does not exist.")

        filename = os.path.basename(file_path)

        if self._is_agol:
            existing_files = self.files
            if any(f.properties.name == filename for f in existing_files):
                raise ValueError(f"File {filename} already exists in the workspace.")

        # Add folder path unless root folder
        full_path = (
            f"{self._folder_name}{filename}" if self._folder_name != "/" else filename
        )

        if self._is_agol:
            url = f"{self._url}/{self._username}/{full_path}"
        else:
            url = f"{self._url}/notebookworkspace/{full_path}"

        headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": str(os.path.getsize(file_path)),
            "x-ms-blob-type": "BlockBlob",
            "x-ms-version": "2020-10-02",  # Consider making this configurable
        }

        resp = self._gis._con.put_raw(
            url, data=open(file_path, "rb"), additional_headers=headers
        )
        return 200 <= resp.status_code < 300

    # ---------------------------------------------------------------------
    def upload(self, fp: str | list[str]) -> list[bool]:
        """
        Uploads a file to the Notebook Server in the current folder.

        ===================     ==========================================================================
        **Parameter**           **Description**
        -------------------     --------------------------------------------------------------------------
        fp                      Required String or list of Strings. Either: the path to the file to upload,
                                a list of paths to the files to upload, or the path to a folder where all
                                the files in the folder will be uploaded under the folder name.
        ===================     ==========================================================================

        :return: List of booleans. True if the file was uploaded, False or an error if it was not.
        """
        # Get files as a list
        files = self._resolve_files(fp)

        if not files:
            raise ValueError(
                "No valid files found to upload. Please provide a valid file path or directory."
            )

        responses = []
        for file in files:
            responses.append(self._upload_single_file(file))
        return responses


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
        self._username = gis.users.me.username
        if not self._check_user_has_workspace(self._username):
            raise ValueError(
                f"User {self._username} does not have a notebook workspace in the organization."
            )

    # --------------------------------------------------------------------
    def __repr__(self):
        return "NotebookDataAccess"

    # ---------------------------------------------------------------------
    def __str__(self):
        return "NotebookDataAccess"

    # ---------------------------------------------------------------------
    @property
    def folders(self) -> List[NotebookFolder]:
        """
        Returns the folders in the workspace directory (/arcgis/home) of the user making the request.

        :return: List[NotebookFolder] - A list of NotebookFolder objects containing the folders in the workspace.
        """
        return _get_folders(
            da=self,
            folder_name=None,
        )

    # ---------------------------------------------------------------------
    @deprecated(deprecated_in="2.4.2", removed_in="2.5.0", current_version="2.4.2")
    @property
    def files(self) -> List[NotebookFile]:
        """
        Lists files that are located in the workspace directory (/arcgis/home) of the user making the request.

        :return: List[NotebookFile] - List of NotebookFile objects
        """
        if self._gis._is_arcgisonline:
            url = f"{self._url}/notebooksWorkspace"
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
    def _check_user_has_workspace(self, username: str) -> bool:
        """
        Checks if the user has a workspace in the organization.

        :param user: User instance or username to check.
        :return: True if the user has a workspace, False otherwise.
        """
        workspace_url = f"{self._url}/listUserWorkspaces".replace("/azureblob/", "/")

        try:
            res = self._gis.session.get(workspace_url, params={"f": "json"}).json()
        except Exception as ex:
            raise RuntimeError(f"Failed to fetch workspaces: {ex}")

        all_workspaces = res.get("Containers", [])
        return any(workspace.get("Name") == username for workspace in all_workspaces)

    # ---------------------------------------------------------------------
    def transfer_workspace(
        self,
        source_user: User | str,
        target_user: User | str | None = None,
        folder_name: str | None = None,
    ) -> bool:
        """
        Transfer the workspace of one user to another user in the organization.
        This can only be done by an administrator.

        This method is useful for transferring the workspace of a user who is leaving the organization to another user.

        ===================  ==========================================================================
        **Parameter**        **Description**
        -------------------  --------------------------------------------------------------------------
        source_user          Required User instance or string. The user or username for which the workspace will be transferred.
        -------------------  --------------------------------------------------------------------------
        target_user          Optional User instance or string. The user or username to which the workspace will be transferred.
                             If not provided, the workspace will be transferred to the current user.
        -------------------  --------------------------------------------------------------------------
        folder_name          Optional String. The name of the folder to which the workspace will be transferred.
                             If not provided, a default name will be used.
        ===================  ==========================================================================

        :return: True if the transfer was successful, False or an error if it was not.
        """
        ### Check if the user is an administrator and can transfer workspaces
        me = self._gis.users.me
        privileges = me.privileges or []
        is_admin = (
            me.role == "org_admin"
            if self._gis._is_arcgisonline
            else "portal:admin:manageServers" in privileges
            and "portal:admin:manageSecurity" in privileges
        )
        if not is_admin:
            raise ValueError(
                "Only organization administrators can transfer user workspaces."
            )

        # Resolve source_user
        if isinstance(source_user, User):
            source_username = source_user.username
        else:
            source_username = source_user
            source_user = self._gis.users.get(source_username)

        # Resolve target_user
        if target_user is None:
            target_user = self._gis.users.me
            target_username = target_user.username
        elif isinstance(target_user, User):
            target_username = target_user.username
        else:
            target_username = target_user
            target_user = self._gis.users.get(target_username)

        # Ensure users exist
        if not source_user or not target_user:
            raise ValueError(
                f"Source user '{source_username}' or target user '{target_username}' does not exist in the organization."
            )

        # Check both users have workspaces
        if not self._check_user_has_workspace(source_username):
            raise ValueError(
                f"Source user '{source_username}' does not have a notebook workspace in the organization."
            )
        if not self._check_user_has_workspace(target_username):
            raise ValueError(
                f"Target user '{target_username}' does not have a workspace in the organization."
            )

        # if folder_name is None, create the default folder name
        if folder_name is None:
            folder_name = f"_transferred_{source_username}"

        url = f"{self._url}/transferUserWorkspace".replace("/azureblob/", "/")
        params = {
            "f": "json",
            "targetFoldername": folder_name,
            "userName": source_username,
        }
        if self._gis._is_arcgisonline:
            params["targetUserName"] = target_username
        else:
            params["targetUsername"] = target_username
        try:
            res = self._gis.session.post(url, params).json()
        except Exception as ex:
            raise RuntimeError(f"Workspace transfer request failed: {ex}")

        if res.get("status") == "success":
            return True
        elif "error" in res:
            raise ValueError(
                f"Error transferring user workspace: {res['error']['message']}"
            )
        else:
            raise ValueError(f"Unknown error during workspace transfer: {res}")

    # ---------------------------------------------------------------------
    @deprecated(deprecated_in="2.4.2", removed_in="2.5.0", current_version="2.4.2")
    def create_folder(self, folder: str) -> bool:
        """
        Create a folder in your `/arcgis/home` notebook workspace directory.

        ===================  ==========================================================================
        **Parameter**         **Description**
        -------------------  --------------------------------------------------------------------------
        folder               Required String. The name of the folder to create. To create a folder in a subfolder,
                             use the format `subfolder1/subfolder2/foldername`. If you want to create a folder
                             in the root directory, use the format `foldername`.
        ===================  ==========================================================================

        """
        if self._gis._is_arcgisonline:
            url = f"{self._url}/{self._username}/createFolder".replace("/azureblob", "")
        else:
            url = f"{self._url}/notebookworkspace/createFolder"
        params = {
            "f": "json",
            "folderName": folder,
            "token": self._gis._con.token,
        }
        return self._gis._con.post(url, params).get("status") == "success"

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
        if self._gis._is_arcgisonline:
            url = f"{self._url}/deleteFile".replace("/azureblob", f"/{self._username}")
        else:
            url = f"{self._url}/notebookworkspace/deleteFile"
        params = {
            "f": "json",
            "fileName": filename,
        }
        return self._gis._con.post(url, params).get("status") == "success"


    # ---------------------------------------------------------------------
    def _resolve_files(self, fp):
        if isinstance(fp, list):
            return [f for f in fp if os.path.isfile(f)]

        if os.path.isdir(fp):
            # If the path is a directory, get all files in the directory
            return [
                os.path.join(fp, f)
                for f in os.listdir(fp)
                if os.path.isfile(os.path.join(fp, f))
            ]

        if os.path.isfile(fp):
            # If the path is a file, return it as a list
            return [fp]

        raise ValueError(
            f"Invalid file path: {fp}. It must be a file or a directory containing files."
        )

    # ---------------------------------------------------------------------
    def _upload_single_file(self, file_path: str, folder: str | None = None) -> bool:
        if not os.path.isfile(file_path):
            raise ValueError(f"File {file_path} does not exist.")

        filename = os.path.basename(file_path)

        if self._gis._is_arcgisonline:
            existing_files = self.files
            if any(f.properties.name == filename for f in existing_files):
                raise ValueError(f"File {filename} already exists in the workspace.")

        full_path = f"{folder}/{filename}" if folder else filename

        if self._gis._is_arcgisonline:
            url = f"{self._url}/{self._username}/{full_path}"
        else:
            url = f"{self._url}/notebookworkspace/{full_path}"

        headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": str(os.path.getsize(file_path)),
            "x-ms-blob-type": "BlockBlob",
            "x-ms-version": "2020-10-02",  # Consider making this configurable
        }

        resp = self._gis._con.put_raw(
            url, data=open(file_path, "rb"), additional_headers=headers
        )
        return 200 <= resp.status_code < 300

    # ---------------------------------------------------------------------
    @deprecated(deprecated_in="2.4.2", removed_in="2.5.0", current_version="2.4.2")
    def upload(self, fp: str | list[str], folder: str | None = None) -> list[bool]:
        """
        Uploads a file to the Notebook Server

        ===================     ==========================================================================
        **Parameter**           **Description**
        -------------------     --------------------------------------------------------------------------
        fp                      Required String or list of Strings. Either: the path to the file to upload,
                                a list of paths to the files to upload, or the path to a folder where all
                                the files in the folder will be uploaded under the folder name.
        -------------------     --------------------------------------------------------------------------
        folder                  Optional String. The name of the folder to upload the file to. If not provided,
                                the file will be uploaded to the root directory of the notebook workspace.
                                Example: `folder1` or `folder1/folder2`.
        ===================     ==========================================================================

        :return: List of booleans. True if the file was uploaded, False or an error if it was not.
        """
        # Get files as a list
        files = self._resolve_files(fp)

        if not files:
            raise ValueError(
                "No valid files found to upload. Please provide a valid file path or directory."
            )

        responses = []
        for file in files:
            responses.append(self._upload_single_file(file, folder))
        return responses
