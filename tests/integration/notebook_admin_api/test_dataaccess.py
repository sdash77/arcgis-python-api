import sys, os

sys.path.insert(0, r"C:\SVN\geosaurus_master_nb_data_access_api\src")
import unittest
from arcgis.gis import GIS

import urllib


gis = GIS(
    url="https://rqawinbi01pt.ags.esri.com/gis",
    username="NBAdvanced",
    password="NBAdvanced.1",
    verify_cert=False,
    trust_env=True,
    proxy=urllib.request.getproxies(),
)
NOTEBOOKS = gis.notebook_server


class TestNotebookDataAccess(unittest.TestCase):
    def test_data_access(self):
        """tests the data access workflow"""
        import tempfile

        fp = os.path.join(tempfile.gettempdir(), "tstore", "dataset.txt")
        os.makedirs(os.path.join(tempfile.gettempdir(), "tstore"), exist_ok=True)
        nb = NOTEBOOKS[0]
        da = nb.data_access
        with open(fp, 'w') as writer:
            writer.write("Hello World!")
            writer.close()
        da.upload(fp)
        assert (
            len(
                [
                    f.properties.name
                    for f in da.files
                    if f.properties.name == 'dataset.txt'
                ]
            )
            > 0
        )
        data = [f for f in da.files if f.properties.name == 'dataset.txt']
        local_file_path = data[0].download()
        assert os.path.isfile(local_file_path)
        os.remove(local_file_path)
        assert data[0].erase()


if __name__ == "__main__":
    unittest.main()
