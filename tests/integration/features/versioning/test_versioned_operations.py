import time
import unittest

from arcgis.features.managers import AttachmentManager
from arcgis.gis import GIS
from arcgis.features._version import VersionManager
from arcgis.features.layer import FeatureLayer

from utils.decorators import integration_test


@integration_test
class TestVersionManagementSQL(unittest.TestCase):
    """Test VersionManagementServer methods"""

    @classmethod
    def setUpClass(cls):
        # Create Python API GIS object and prepare REST service URL strings
        cls.base_server_url = "https://pythonapitestnb.dev.geocloud.com/server/rest/services/BranchVersionedFeatureService/"
        cls.gis = GIS(
            "https://pythonapitestnb.dev.geocloud.com/portal/",
            "api_data_owner",
            "geosaurus_donot3xpose",
            verify_cert=False,
        )
        endpoints = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url + url for url in endpoints}

        cls.bv_feature_layer = FeatureLayer(
            f"{cls.service_urls['FeatureServer']}/0", cls.gis
        )
        cls.vms = VersionManager(cls.service_urls["VersionManagementServer"], cls.gis)
        cls.timestamp = int(time.time())

    def test_query_attachments_in_bv(self):
        version = self.vms.get("API_DATA_OWNER.Edit_Version_1")
        am = AttachmentManager(layer=self.bv_feature_layer, version=version)
        existing_attachments = am.get_list(oid=101)
        self.assertEqual(
            2,
            len(existing_attachments),
            "Incorrect quantity of attachments found in version",
        )


if __name__ == "__main__":
    unittest.main()
