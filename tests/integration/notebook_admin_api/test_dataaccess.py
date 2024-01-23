import sys, os

# sys.path.insert(0, r"C:\SVN\geosaurus_master\src")
import unittest
from arcgis.gis import GIS
from arcgis.auth.tools._util import detect_proxy
import urllib
from utils.decorators import integration_test

GIS(
    url="https://datasciencedev.esri.com/portal",
    username="portaladmin",
    password="esri.agp",
    verify_cert=False,
    trust_env=True,
    use_gen_token=True,
    proxy=detect_proxy(True),
).users.me.update(security_question=1, security_answer="TheAnswerIs5")


gis = GIS(
    url="https://datasciencedev.esri.com/portal",
    username="portaladmin",
    password="esri.agp",
    verify_cert=False,
    trust_env=True,
    proxy=detect_proxy(True),
)
NOTEBOOKS = gis.notebook_server


@integration_test
class TestNotebookDataAccess(unittest.TestCase):
    def test_data_access(self):
        """tests the data access workflow"""
        import tempfile

        fp = os.path.join(tempfile.gettempdir(), "tstore", "dataset.txt")
        os.makedirs(os.path.join(tempfile.gettempdir(), "tstore"), exist_ok=True)
        nb = NOTEBOOKS[0]
        da = nb.data_access
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
