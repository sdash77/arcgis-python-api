import os
import tempfile
import unittest
from utils.decorators import integration_test, profiles
from arcgis.gis.nb._dataaccess import NotebookDataAccess, NotebookFolder, NotebookFile


@profiles.admin_enterprise_and_agol
@integration_test
class TestNotebookDataAccess(unittest.TestCase):
    def setUp(self):
        # Assumes self.gis is set by the profile decorator
        self.nb_server = self.gis.notebook_server[0]
        self.da = self.nb_server.data_access

    def test_folders_property(self):
        folders = self.da.folders
        self.assertIsInstance(folders, list)
        self.assertTrue(any(isinstance(f, NotebookFolder) for f in folders))
        self.assertEqual(folders[0].name, "Home")

    def test_create_and_rename_folder(self):
        home = self.da.folders[0]
        new_folder = home.create_folder("testfolder")
        self.assertIsInstance(new_folder, NotebookFolder)
        self.assertEqual(new_folder.name, "testfolder")
        # Rename
        renamed = new_folder.rename("testfolder_renamed")
        self.assertTrue(renamed)
        self.assertEqual(new_folder.name, "testfolder_renamed")
        # Clean up
        self.assertTrue(new_folder.delete())

    def test_folder_files_and_upload(self):
        home = self.da.folders[0]
        # Create a temp file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "test_upload.txt")
        with open(file_path, "w") as f:
            f.write("NotebookDataAccess test upload.")
        # Upload
        upload_result = home.upload(file_path)
        self.assertTrue(all(upload_result))
        # Check file exists in files
        files = home.files
        self.assertTrue(any(f.name == "test_upload.txt" for f in files))
        # Download and delete
        file_obj = next(f for f in files if f.name == "test_upload.txt")
        local_path = file_obj.download()
        self.assertTrue(os.path.isfile(local_path))
        self.assertTrue(file_obj.delete())
        os.remove(local_path)

    def test_move_folder(self):
        home = self.da.folders[0]
        folder1 = home.create_folder("move_src")
        folder2 = home.create_folder("move_dest")
        # Move folder1 into folder2
        moved = folder1.move(folder2)
        self.assertTrue(moved)
        # Clean up
        self.assertTrue(folder1.delete())
        self.assertTrue(folder2.delete())

    def test_transfer_workspace(self):
        # Only run if user is admin and there is more than one user with a workspace
        users = [
            u
            for u in self.gis.users.search()
            if self.da._check_user_has_workspace(u.username)
        ]
        if len(users) < 2:
            self.skipTest(
                "Not enough users with workspaces to test transfer."
            )
        source = users[0]
        target = users[1]
        result = self.da.transfer(source, target)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
