import sys, os
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles

PROXIES = detect_proxy(True)  # Handles Fiddler when True


@profiles.admin_enterprise
@integration_test
class Test_SymbolService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        cls._item = cls.gis.content.get("587a104e92a24a37abb9b4e4112917f2")

    def test_symbol_server(self):
        assert self.gis.symbol_service

    def test_symbol_server_properties(self):
        assert self.gis.symbol_service.properties

    def test_generate_symbol(self):
        import requests, tempfile, os

        ss = self.gis.symbol_service

        fp = os.path.join(tempfile.gettempdir(), "batman.svg")
        r = requests.get("https://www.svgrepo.com/show/303233/batman-5-logo.svg")
        with open(fp, "w") as writer:
            writer.write(r.text)
        res = ss.generate_symbol(fp)
        assert res
        assert isinstance(res, dict)

    def test_generate_image(self):

        if self._item:

            ss = self.gis.symbol_service
            res = ss.generate_image(self._item, "Point symbol")
            assert os.path.isfile(res)

    def test_generate_image_fp(self):
        os.makedirs("./tempfolder", exist_ok=True)
        if self._item:

            ss = self.gis.symbol_service
            res = ss.generate_image(
                self._item,
                "Point symbol",
                file_path=r"./tempfolder/myfile.png",
            )
            assert os.path.isfile(res)


if __name__ == "__main__":
    unittest.main()
