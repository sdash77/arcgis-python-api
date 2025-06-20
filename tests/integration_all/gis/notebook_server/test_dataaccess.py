import os
import unittest
from utils.decorators import integration_test, profiles
from arcgis.gis import GIS


@profiles.admin_enterprise
@integration_test
class TestNotebookDataAccess(unittest.TestCase):

    def test_data_access(self):
        """tests the data access workflow"""
        import tempfile

        NOTEBOOKS = self.gis.notebook_server

        fp = os.path.join(tempfile.gettempdir(), "tstore", "dataset.txt")
        os.makedirs(
            os.path.join(tempfile.gettempdir(), "tstore"), exist_ok=True
        )
        nb = NOTEBOOKS[0]
        da = nb.data_access
        da.create_folder("helloworld")
        with open(fp, "w") as writer:
            writer.write("Hello World!")
            writer.close()
        da.upload(fp)
        assert (
            len(
                [
                    f.properties.name
                    for f in da.files
                    if f.properties.name == "dataset.txt"
                ]
            )
            > 0
        )
        data = [f for f in da.files if f.properties.name == "dataset.txt"]
        local_file_path = data[0].download()
        assert os.path.isfile(local_file_path)
        os.remove(local_file_path)
        assert data[0].erase()


if __name__ == "__main__":
    unittest.main()
