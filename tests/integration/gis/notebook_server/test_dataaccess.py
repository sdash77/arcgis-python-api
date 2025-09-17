import os
import uuid
import tempfile
import unittest
from utils.decorators import integration_test, profiles
from arcgis.gis import GIS
from arcgis.gis.nb._dataaccess import DATAACCESSTYPE, NotebookFolder, NotebookFile, NotebookDataAccess
from integration.config import get_resource_path
from utils._logging import enable_verbose_logging


enable_verbose_logging()


@profiles.admin_enterprise_and_agol
@integration_test
class TestNotebookDataAccess(unittest.TestCase):

    def setUp(self):
        self.nb_server = self.gis.notebook_server[0]

        # check if workspace is available
        if self.nb_server.data_access._check_user_has_workspace(username=self.gis.users.me):
            self.da = self.nb_server.data_access
        else:
            self.da = self._set_workspace(self.gis)

    def _set_workspace(self, gis) -> NotebookDataAccess:
        if gis._is_agol:
            nb_id = "44cb2b96893d472c8a5456e4f7baadcc"
            open_notebook = gis.notebook_server[0].notebooksmanager.open_notebook(nb_id)
        else:
            nb_id = "15f9a363d84141768c34a7a59a111db5"
            open_notebook = gis.notebook_server[0].notebooks.open_notebook(nb_id)
        if open_notebook["status"] == "COMPLETED":
            return gis.notebook_server[0].data_access

    def test_folders_property(self):
        folders = self.da.folders
        self.assertIsInstance(folders, list)
        self.assertTrue(any(isinstance(f, NotebookFolder) for f in folders))
        self.assertEqual(folders[0].name, "Home")

    def test_create_and_rename_folder(self):
        """ Test workflow: creating a folder in workspace /home and renaming it."""

        if self.gis.version <= [2025, 1]:
            self.skipTest("Notebook Data Access features are fully supported in [2025, 2] versions and above.")

        folder = None
        try:
            # access home folder and create a folder
            home = self.da.folders[0]
            home.create_folder("testfolder")

            # get folder
            folder = self.da.get("testfolder", DATAACCESSTYPE.FOLDER)
            self.assertIsInstance(folder, NotebookFolder)
            self.assertEqual(folder.name, "testfolder")

            # Rename
            renamed = folder.rename("testfolder_renamed")
            self.assertTrue(renamed)
            self.assertEqual(folder.name, "testfolder_renamed")

        finally:
            if folder:
                folder.delete()

    def test_create_and_rename_file(self):
        """ Test workflow: upload a file in workspace /home and renaming it."""

        if self.gis.version <= [2025, 1]:
            self.skipTest("Notebook Data Access features are fully supported in [2025, 2] versions and above.")

        file = None
        try:
            # access home folder and create a folder
            home = self.da.folders[0]
            self.file_name = "USA_Major_Cities.zip"
            fp = get_resource_path(f"staging_data/{self.file_name}")
            home.upload(fp)

            # get file
            file = self.da.get(self.file_name, DATAACCESSTYPE.FILE)
            self.assertIsInstance(file, NotebookFile)
            self.assertEqual(file.name, self.file_name)

            # Rename
            self.rename = f"renamed_{self.file_name}"
            renamed = file.rename(self.rename)
            self.assertTrue(renamed)
            self.assertTrue(self.da.get(self.rename, DATAACCESSTYPE.FILE))

        finally:
            if self.da.get(self.rename, DATAACCESSTYPE.FILE):
                self.da.get(self.rename, DATAACCESSTYPE.FILE).delete()

    def test_folder_files_and_upload(self):
        """ Test workflow: uploading a text file to a folder in /home and downloading it."""

        file_obj = None
        local_path = None
        try:
            # access home folder
            home = self.da.folders[0]

            # Create a temp file
            file_name = f"test_upload_{uuid.uuid4().hex[:4]}.txt"
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, file_name)
            with open(file_path, "w") as f:
                f.write("NotebookDataAccess test upload.")

            # Upload
            upload_result = home.upload(file_path)
            self.assertTrue(all(upload_result))

            # Check file exists in files
            files = home.files
            self.assertTrue(any(f.name == file_name for f in files))

            # Test get file
            file_obj = self.da.get(file_name, DATAACCESSTYPE.FILE)
            self.assertIsInstance(file_obj, NotebookFile)
            self.assertEqual(file_obj.name, file_name)

            # Download and delete
            file_obj = next(f for f in files if f.name == file_name)
            local_path = file_obj.download()
            self.assertTrue(os.path.isfile(local_path))

        finally:
            if file_obj:
                file_obj.delete()
            if local_path:
                os.remove(local_path)

    def test_move_file(self):
        """ Test workflow: moving a folder to another folder in workspace."""

        if self.gis.version <= [2025, 1]:
            self.skipTest("Notebook Data Access features are fully supported in [2025, 2] versions and above.")

        folder = None
        try:
            file_name = "USA_Major_Cities.zip"
            file = get_resource_path(f"staging_data/{file_name}")

            home = self.da.folders[0]
            file_uploaded = home.upload(file)
            folder = home.create_folder(f"move_file_dest")

            # Move file into folder
            file = self.da.get(file_name, DATAACCESSTYPE.FILE)
            moved = file.move(folder)
            self.assertTrue(moved)
            self.assertTrue(folder.files[0].name, file_name)

        finally:
            if folder:
                folder.delete()

    def test_move_folder(self):
        """ Test workflow: moving a folder to another folder in workspace."""

        if self.gis.version <= [2025, 1]:
            self.skipTest("Notebook Data Access features are fully supported in [2025, 2] versions and above.")

        folder1 = None
        folder2 = None
        try:
            file_name = "USA_Major_Cities.zip"
            file = get_resource_path(f"staging_data/{file_name}")

            home = self.da.folders[0]
            folder1 = home.create_folder(f"move_src")
            file_uploaded = folder1.upload(file)
            self.assertTrue(file_uploaded[0], "File upload failed")
            folder2 = home.create_folder(f"move_dest")

            # Move folder1 into folder2
            moved = folder1.move(folder2)
            self.assertTrue(moved)
            self.assertEqual(folder2.folders[0].name, folder1.name)
            self.assertIn(file_name.split(".")[0], folder2.folders[0].files[0].name)

        finally:
            # AGOL deletes the source folder automatically after moving, whereas Enterprise does not
            if self.da.get(folder2.name):
                folder2.delete()
            if not self.gis._is_agol and folder1:
                folder1.delete()

    def test_transfer_workspace(self):
        """ Test workflow: transferring workspace from one user to another."""

        user_src = None
        try:
            # create a new user and access its workspace
            username = f"nbda_user_{uuid.uuid4().hex[:4]}"
            password = "IL0veMyGI$_4Ever"
            new_password = "IL0veMyGI$_4Ever_1"
            user_src = self.gis.users.create(
                username=username,
                password=password,
                firstname="user",
                lastname="geosaurus",
                email="user@esri.com",
                user_type="creator",
                role="org_publisher",
            )
            user_src.update_role(role="org_admin")
            user_src.reset(password=password, new_password=new_password, new_security_question='1', new_security_answer="redlands")
            user_src_gis = GIS(url=self.gis.url, username=username, password=new_password)

            # access notebook to enable data access
            user_da = self._set_workspace(user_src_gis)

            # create file and folder in user workspace
            fp = get_resource_path("staging_data/USA_Major_Cities.zip")
            file = user_da.folders[0].upload(fp)
            folder = user_da.folders[0].create_folder("transfer_folder")

            # transfer
            result = self.da.transfer(user_src, self.gis.users.me)
            self.assertTrue(result)

        finally:
            if user_src:
                user_src.delete()
            if self.da.get(f"_transferred_{user_src.username}", DATAACCESSTYPE.FILE):
                self.da.get(f"_transferred_{user_src.username}", DATAACCESSTYPE.FILE).delete()


if __name__ == "__main__":
    unittest.main()