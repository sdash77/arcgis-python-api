import os
import uuid
import tempfile
import unittest
from utils.decorators import integration_test, profiles
from arcgis.gis.nb._dataaccess import DATAACCESSTYPE, NotebookFolder, NotebookFile


@profiles.admin_enterprise_and_agol
@integration_test
class TestNotebookDataAccess(unittest.TestCase):

    def setUp(self):
        self.nb_server = self.gis.notebook_server[0]

        # check if workspace is available
        try:
            self.da = self.nb_server.data_access
        except Exception as e:
            self.skipTest("NotebookDataAccess is either empty or not accessible in this environment.")

    def test_folders_property(self):
        folders = self.da.folders
        self.assertIsInstance(folders, list)
        self.assertTrue(any(isinstance(f, NotebookFolder) for f in folders))
        self.assertEqual(folders[0].name, "Home")

    def test_create_and_rename_folder(self):
        """ Test workflow: creating a folder in workspace and renaming it."""

        new_folder = None
        try:
            home = self.da.folders[0]
            new_folder = home.create_folder("testfolder")
            self.assertIsInstance(new_folder, NotebookFolder)
            self.assertEqual(new_folder.name, "testfolder")

            # Test getting the folder
            fetched_folder = self.da.get("testfolder", DATAACCESSTYPE.FOLDER)
            self.assertIsInstance(fetched_folder, NotebookFolder)
            self.assertEqual(fetched_folder.name, "testfolder")

            # Rename
            renamed = new_folder.rename("testfolder_renamed")
            self.assertTrue(renamed)
            self.assertEqual(new_folder.name, "testfolder_renamed")

        except Exception as e:
            raise e

        finally:
            self.assertTrue(new_folder.delete())

    def test_folder_files_and_upload(self):
        """ Test workflow: uploading a file to a folder in workspace and downloading it."""

        file_obj = None
        local_path = None
        try:
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

            # Test getting the file
            file_obj = self.da.get(file_name, DATAACCESSTYPE.FILE)
            self.assertIsInstance(file_obj, NotebookFile)
            self.assertEqual(file_obj.name, file_name)

            # Download and delete
            file_obj = next(f for f in files if f.name == file_name)
            local_path = file_obj.download()
            print(local_path)
            self.assertTrue(os.path.isfile(local_path))

        except Exception as e:
            raise e

        finally:
            self.assertTrue(file_obj.delete())
            os.remove(local_path)

    def test_move_folder(self):
        """ Test workflow: moving a folder to another folder in workspace."""

        folder2 = None
        try:
            home = self.da.folders[0]
            folder1 = home.create_folder(f"move_src_{uuid.uuid4().hex[:4]}")
            folder2 = home.create_folder(f"move_dest_{uuid.uuid4().hex[:4]}")

            # Move folder1 into folder2
            moved = folder1.move(folder2)
            self.assertTrue(moved)

        except Exception as e:
            raise e

        finally:
            self.assertTrue(folder2.delete())

    @unittest.skip("This workflow cannot be automated")
    def test_transfer_workspace(self):
        # Only run if user is admin and there is more than one file/folder with a workspace
        # The source user will have empty workspace after transferring, so we have no way to automatically get source workspace back
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
