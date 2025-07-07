import unittest
import time
import concurrent.futures
from arcgis.gis import GIS
from arcgis.features._parcel import ParcelFabricManager
from arcgis.features.layer import FeatureLayerCollection
from utils.decorators import integration_test
from . import parcel_fabric_utils as pfutils


@integration_test
class TestVersionManager(unittest.TestCase):
    """Reassign parcels to a different record"""

    vms = None
    gis = None
    services = None
    service_urls = {}
    version_name = None
    base_server_url = None
    parcel_fabric_flc = None

    @classmethod
    def setUpClass(cls):
        # Create Python API GIS object and prepare REST service URL strings
        cls.base_server_url = (
            "https://dev0016752.esri.com/server/rest/services/WashingtonCountyLSA/"
        )
        cls.gis = GIS(
            "https://dev0016752.esri.com/portal/",
            "admin",
            "esri.agp",
            verify_cert=False,
        )
        endpoints = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url + url for url in endpoints}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis
        )

        cls.vms = cls.parcel_fabric_flc.versions

        cls.records_fl = pfutils.get_feature_layer(cls.parcel_fabric_flc, "Records")

        cls.timestamp = int(time.time())
        cls.record_name = f"api-{cls.timestamp}"

    def test_create_version_reconcile_async(self):
        _version_name_txt = "api-{}".format(int(time.time()))
        self.vms.create(_version_name_txt)
        fq_version_name = f"admin.{_version_name_txt}"

        with self.vms.get(fq_version_name, "read") as version:
            version.mode = "edit"
            result = version.reconcile(
                end_with_conflict=True,
                conflict_detection="byAttribute",
                with_post=False,
                future=True,
            )
            assert isinstance(result, concurrent.futures.Future)
            result = result.result()
            self.assertEqual(
                "Completed", result["status"], f"Async job failed:\t{result['status']}"
            )
            print(result)

    def test_reconcile_post_async(self):
        _version_name_txt = "api-{}".format(int(time.time()))
        self.vms.create(_version_name_txt)
        fq_version_name = f"admin.{_version_name_txt}"

        # Add a single feature to a feature layer
        new_feature = pfutils.create_parcel_record(
            self.parcel_fabric_flc, fq_version_name, f"api-{self.timestamp}"
        )

        self.assertIsNotNone(new_feature.get("addResults"), "Did not insert a feature")

        with self.vms.get(fq_version_name, "read") as version:
            version.mode = "edit"
            result = version.reconcile(
                end_with_conflict=True,
                conflict_detection="byAttribute",
                with_post=False,
                future=True,
            )
            assert isinstance(result, concurrent.futures.Future)
            result = result.result()
            self.assertEqual(
                "Completed", result["status"], f"Async job failed:\t{result['status']}"
            )

            did_post = version.post()
            self.assertTrue(did_post, "Posting to default failed")

    @classmethod
    def tearDownClass(cls):
        pfutils.clean_up_versions(cls.vms)


if __name__ == "__main__":
    unittest.main()
