import logging
import sys
import unittest
from arcgis.features._topographic import TopographicProductionManager
from arcgis.gis import GIS
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis.server.catalog import ServicesDirectory

__logger__ = logging.getLogger()

def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)
url = "https://rextapilnxsvr01.esri.com/server"
username = "siteadmin"
password = "esri.agp2"

class TestTopographicProductionManager(unittest.TestCase):
    """Tests the Topographic Production Service"""

    def add_product(self):
        sd = ServicesDirectory(
            url=url,
            username=username,
            password=password,
            verify_cert=False,
            proxy=PROXIES,
        )
        # Automate the setup
        sd.admin.publish_sd()


if __name__ == "__main__":
    unittest.main()