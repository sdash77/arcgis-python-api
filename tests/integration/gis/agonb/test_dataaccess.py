import os
import unittest
import uuid

from utils.data_utils import cleanup_published_items
from integration.config import get_resource_path
from utils.decorators import integration_test, profiles


@profiles.admin_enterprise_and_agol
@integration_test
class TestAGOLNotebookDataAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._nbm = cls.gis.notebook_server[0]
        cls._da = cls._nbm.data_access
        cls.items = []

    def setUp(self):
        self.capitals_csv = get_resource_path(
            "mapping/capitals_tbl.csv", unique_copy=True
        )
        self.restaurants_csv = get_resource_path(
            "mapping/restaurants.xlsx", unique_copy=True
        )

    def test_file_upload_and_delete(self):
        # Upload single file
        result = self._da.upload(self.capitals_csv)
        self.assertTrue(all(result), "Upload failed for one or more files")

        self.items.append(result)
        file_basename = os.path.basename(self.capitals_csv)

        # Validate file exists
        files = [f.properties.name for f in self._da.files]
        self.assertIn(file_basename, files)

        # Delete the uploaded file
        file_obj = next(f for f in self._da.files if f.properties.name == file_basename)
        deleted = file_obj.delete()
        self.assertTrue(deleted, "Failed to delete uploaded file")

    def test_upload_folder(self):
        # Move uniquely named files into a temp folder for upload
        capitals_basename = os.path.basename(self.capitals_csv)
        capitals_path = os.path.dirname(self.capitals_csv)
        restaurants_basename = os.path.basename(self.restaurants_csv)
        os.rename(
            self.restaurants_csv, os.path.join(capitals_path, restaurants_basename)
        )
        test_folder = capitals_path

        try:
            result = self._da.upload(test_folder)
            self.assertTrue(result, "Folder upload did not succeed")
            self.items.append(result)

            files = [f.properties.name for f in self._da.files]
            self.assertIn(capitals_basename, files)
            self.assertIn(restaurants_basename, files)
        finally:
            # Cleanup
            for fname in [capitals_basename, restaurants_basename]:
                file_obj = next(
                    (f for f in self._da.files if f.properties.name == fname), None
                )
                if file_obj:
                    self.assertTrue(file_obj.delete(), f"Failed to delete {fname}")

    def test_rename_file(self):
        # Upload file
        uid = uuid.uuid4().hex[:6]
        csv_basename = os.path.basename(self.capitals_csv)
        new_csv_basename = f"capitals_renamed_{uid}.csv"

        try:
            result = self._da.upload(self.capitals_csv)
            self.assertTrue(result, "Failed to upload item")
            self.items.append(result)

            file_obj = next(
                f for f in self._da.files if f.properties.name == csv_basename
            )

            # Rename file
            renamed = file_obj.rename(new_csv_basename)
            self.assertTrue(renamed, "Failed to rename file")

            # Confirm rename
            files = [f.properties.name for f in self._da.files]
            self.assertIn(new_csv_basename, files)
        finally:
            # Cleanup
            renamed_file = next(
                f for f in self._da.files if f.properties.name == new_csv_basename
            )
            self.assertTrue(renamed_file.delete(), "Failed to delete renamed file")

    @unittest.skip("Check download capability")
    def test_download_file(self):
        # Upload a file
        csv_basename = os.path.basename(self.capitals_csv)
        result = self._da.upload(self.capitals_csv)
        self.assertTrue(result, "Failed to upload item")
        self.items.append(result)

        file_obj = next(f for f in self._da.files if f.properties.name == csv_basename)

        # Download file
        local_path = file_obj.download()
        self.assertTrue(
            os.path.exists(local_path),
            f"Downloaded file does not exist locally: {local_path}",
        )

        # Cleanup
        self.assertTrue(file_obj.delete(), "Failed to delete file after download")
        os.remove(local_path)

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items(cls.items)


if __name__ == "__main__":
    unittest.main()
