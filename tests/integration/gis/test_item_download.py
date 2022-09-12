import sys

#
#  Update the Path to set the test area
sys.path.insert(0, r"C:\SVN\geosaurus_master_issue_8163\src")
import logging, tempfile
import unittest, os
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


profiles = [None]
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


class Test_ItemDownload(unittest.TestCase):
    def test_download_anonymous(self):
        """tests downloading a file with no auth"""
        gis = GIS(verify_cert=False, proxy=PROXIES)
        item = gis.content.get("8b4600eb9a29407bbfe51491ad5bf62c")
        filepath = item.download(tempfile.gettempdir())
        assert os.path.isfile(filepath)
        if os.path.isfile(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    unittest.main()
