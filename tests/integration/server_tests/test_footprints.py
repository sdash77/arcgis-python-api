import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.gis.server import ServicesDirectory
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


profiles = ['your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestServicesDirectory(unittest.TestCase):
    def test_footprints(self):
        """tests the general footprint call"""
        sd = ServicesDirectory(
            url="https://sampleserver6.arcgisonline.com/arcgis/rest/services"
        )
        res = sd.footprints()

        assert res

    def test_footprints_folder(self):
        """tests the general footprint call"""
        sd = ServicesDirectory(
            url="https://sampleserver6.arcgisonline.com/arcgis/rest/services"
        )
        res = sd.footprints(folder=sd.folders[0])
        assert res

    def test_footprints_out_sr(self):
        """tests the general footprint call"""
        sd = ServicesDirectory(
            url="https://sampleserver6.arcgisonline.com/arcgis/rest/services"
        )
        res = sd.footprints(out_sr=4326)
        assert res


if __name__ == "__main__":
    unittest.main()
