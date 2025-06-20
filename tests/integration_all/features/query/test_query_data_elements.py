import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis.server.catalog import ServicesDirectory
from arcgis.features import FeatureLayerCollection
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)


PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestQueryDataElements(unittest.TestCase):
    def test_query_data_elements(self):
        sd = ServicesDirectory(
            url="https://sampleserver7.arcgisonline.com/server/rest/services",
            username='viewer01',
            password='I68VGU^nMurF',
        )
        services = sd.list("UtilityNetwork")
        for service in services:
            if (
                isinstance(service, FeatureLayerCollection)
                and "supportsQueryDataElements" in service.properties
                and service.properties.supportsQueryDataElements
                and len(service.layers) > 0
            ):
                break

        resp = service.query_data_elements(
            [lyr.properties.id for lyr in service.layers]
        )
        assert isinstance(resp, dict)


if __name__ == "__main__":
    unittest.main()
