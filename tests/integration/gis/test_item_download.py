import sys
import logging, tempfile
import unittest, os
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = [None]
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class Test_ItemDownload(unittest.TestCase):
    def test_download_anonymous(self):
        """tests downloading a file with no auth"""
        gis = GIS(verify_cert=False, proxy=PROXIES)
        item = gis.content.get("b7addc908a58486dbc0253b052140d45")
        filepath = item.download(tempfile.gettempdir())
        assert os.path.isfile(filepath)
        if os.path.isfile(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    unittest.main()
