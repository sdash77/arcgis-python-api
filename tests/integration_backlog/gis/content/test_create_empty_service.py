import sys
import logging, uuid
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.auth import ArcGISProAuth, EsriWindowsAuth
from arcgis.features import FeatureLayerCollection
from arcgis.gis import GIS, Item
from arcgis.gis import CreateServiceParameter
from arcgis.gis._impl import ServiceTypeEnum
from utils.decorators import integration_test

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


@integration_test
class TestCreateEmptyService(unittest.TestCase):
    def test_service_type_enum(self):
        assert ServiceTypeEnum.FEATURE_SERVICE.value == "featureService"
        assert ServiceTypeEnum.IMAGE_SERVICE.value == "imageService"
        assert ServiceTypeEnum.RELATIONSHIP_SERVICE.value == "relationalCatalogService"

    def test_create_empty_service(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            cp = CreateServiceParameter(
                name="testemptyservice2", output_type=ServiceTypeEnum.FEATURE_SERVICE
            )
            res = gis.content.create_empty_service(cp)
            assert res.delete()


if __name__ == "__main__":
    unittest.main()
