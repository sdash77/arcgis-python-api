import sys

#
#  Update the Path to set the test area
sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import logging, uuid
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)


profiles = ["your_online_profile", "your_enterprise_profile"]
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


class Test_UXClass(unittest.TestCase):
    """Tests UX Class"""


class Test_HomePageEditorClass(unittest.TestCase):
    """Tests Home Page Editor Class"""


class Test_OrgMapSettingsClass(unittest.TestCase):
    """Tests Org Map Settings Class"""


if __name__ == "__main__":
    unittest.main()
