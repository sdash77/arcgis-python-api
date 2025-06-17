import os
import unittest
from integration.config import get_resource_path
from utils.decorators import integration_test, profiles

CAPITALS_CSV = get_resource_path("mapping/capitals_tbl.csv")
RESTAURANTS_XLSX = get_resource_path("mapping/restaurants.xlsx")


@profiles.admin_agol
@integration_test
class TestAGOLNotebookDataAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._nbm = cls.gis.notebook_server[0]
        cls._da = cls._nbm.data_access

    def test_file_upload_and_delete(self):
        # Upload single file
        result = self._da.upload(CAPITALS_CSV)
        self.assertTrue(all(result), "Upload failed for one or more files")

        # Validate file exists
        files = [f.properties.name for f in self._da.files]
        self.assertIn("capitals_tbl.csv", files)

        # Delete the uploaded file
        file_obj = next(
            f for f in self._da.files if f.properties.name == "capitals_tbl.csv"
        )
        deleted = file_obj.delete()
        self.assertTrue(deleted, "Failed to delete uploaded file")

    def test_upload_folder(self):
        test_folder = "test/integration/resources/mapping"
        result = self._da.upload(test_folder)
        self.assertTrue(result, "Folder upload did not succeed")

        files = [f.properties.name for f in self._da.files]
        self.assertIn("capitals_tbl.csv", files)
        self.assertIn("restaurants.xlsx", files)

        # Cleanup
        for fname in ["capitals_tbl.csv", "restaurants.xlsx"]:
            file_obj = next(
                (f for f in self._da.files if f.properties.name == fname), None
            )
            if file_obj:
                self.assertTrue(file_obj.delete(), f"Failed to delete {fname}")

    def test_rename_file(self):
        # Upload file
        self.assertTrue(all(self._da.upload(CAPITALS_CSV)))
        file_obj = next(
            f for f in self._da.files if f.properties.name == "capitals_tbl.csv"
        )

        # Rename file
        renamed = file_obj.rename("capitals_renamed.csv")
        self.assertTrue(renamed, "Failed to rename file")

        # Confirm rename
        files = [f.properties.name for f in self._da.files]
        self.assertIn("capitals_renamed.csv", files)

        # Cleanup
        renamed_file = next(
            f for f in self._da.files if f.properties.name == "capitals_renamed.csv"
        )
        self.assertTrue(renamed_file.delete(), "Failed to delete renamed file")

    def test_download_file(self):
        # Upload a file
        self.assertTrue(all(self._da.upload(CAPITALS_CSV)))
        file_obj = next(
            f for f in self._da.files if f.properties.name == "capitals_tbl.csv"
        )

        # Download file
        local_path = file_obj.download()
        self.assertTrue(
            os.path.exists(local_path), "Downloaded file does not exist locally"
        )

        # Cleanup
        self.assertTrue(file_obj.delete(), "Failed to delete file after download")
        os.remove(local_path)


if __name__ == "__main__":
    unittest.main()
