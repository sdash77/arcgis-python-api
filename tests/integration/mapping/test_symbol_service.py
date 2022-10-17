import sys, os

#
#  Update the Path to set the test area
# sys.path.insert(0, r"C:\SVN\geosaurus_master_issue_7959\src")
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile', 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


class Test_SymbolService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._gis = GIS(
            url="https://rpubs22001.ags.esri.com/portal",
            username='PAPIadmin',
            password="PAPIletmein01",
            verify_cert=False,
            proxy=PROXIES,
        )
        cls._item = cls._gis.content.get("f82c7d873a92411f8b407062436c9afd")

    def test_symbol_server(self):
        assert self._gis.symbol_service

    def test_symbol_server_properties(self):
        assert self._gis.symbol_service.properties

    def test_generate_symbol(self):
        ss = self._gis.symbol_service
        res = ss.generate_symbol(r"c:/temp/batman.svg")
        assert res
        assert isinstance(res, dict)

    def test_generate_image(self):

        if self._item:

            ss = self._gis.symbol_service
            res = ss.generate_image(self._item, "Point symbol")
            assert os.path.isfile(res)

    def test_generate_image_fp(self):
        os.makedirs("./tempfolder", exist_ok=True)
        if self._item:

            ss = self._gis.symbol_service
            res = ss.generate_image(
                self._item,
                "Point symbol",
                file_path=r"./tempfolder/myfile.png",
            )
            assert os.path.isfile(res)


if __name__ == "__main__":
    unittest.main()
