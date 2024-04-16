import unittest
from arcgis.gis import GIS
from arcgis.features.layer import FeatureLayerCollection
from utils.decorators import integration_test
from . import parcel_fabric_utils as pfutils


@integration_test
class TestParcelFabricRecords(unittest.TestCase):
    """Apply LSA on a small fabric.  Test sync and async"""

    vms = None
    gis = None
    service_urls = {}
    parcel_fabric_flc = None
    base_server_url = None

    @classmethod
    def setUpClass(cls):
        # Create Python API GIS object and prepare REST service URL strings
        cls.base_server_url = (
            "https://krennic.esri.com/server/rest/services/WashingtonCountyLSA/"
        )
        cls.gis = GIS(
            "https://krennic.esri.com/portal/", "admin", "esri.agp", verify_cert=False
        )
        endpoints = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url + url for url in endpoints}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis
        )
        cls.vms = cls.parcel_fabric_flc.versions
        cls.version_name = pfutils.create_version(cls.vms)
        cls.records_service_url = f"{cls.service_urls['FeatureServer']}/1"

    def test_create_new_record_applyEdits(self):
        new_record = pfutils.create_parcel_record(
            self.parcel_fabric_flc, self.version_name, "API-Record"
        )

        record_guid = new_record["addResults"][0]["globalId"].lower()
        search_record = pfutils.get_record_by_guid(
            self.gis, self.records_service_url, record_guid, self.version_name
        )

        self.assertIsNotNone(search_record, "dang it")

    def test_create_a_record_then_search(self):
        cbr = "{4B753DC5-AEDD-4703-AE56-B236EBB5DEFB}".lower()
        search_tax = pfutils.query_service(
            url=self.service_urls["FeatureServer"],
            fl_id=15,
            gis=self.gis,
            where=f"CREATEDBYRECORD = '{cbr}'",
            out_fields=["Name", "GlobalID"],
            version_name=self.version_name,
        )
        self.assertEqual(
            12, len(search_tax), "Incorrect quantity of features in query result"
        )

    @classmethod
    def tearDownClass(cls):
        pfutils.clean_up_versions(cls.vms)


if __name__ == "__main__":
    unittest.main()
