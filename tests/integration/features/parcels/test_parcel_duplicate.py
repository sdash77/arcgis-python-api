import unittest
import concurrent.futures
from arcgis.gis import GIS
from arcgis.features._parcel import ParcelFabricManager
from arcgis.features.layer import FeatureLayerCollection
from utils.decorators import integration_test, profiles
from . import parcel_fabric_utils as pfutils


@profiles.parcel_fabric
@integration_test
class TestDuplicateParcels(unittest.TestCase):
    """Duplicate parcels"""

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

        endpoints = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url + url for url in endpoints}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis
        )
        cls.vms = cls.parcel_fabric_flc.versions

    def test_duplicate_one_parcel_into_condiv_increment_field(self):
        fq_version_name = pfutils.create_version(self.vms)
        existing_record = pfutils.get_record_guid_by_name(
            self.gis,
            f"{self.service_urls['FeatureServer']}/1",
            "Record001",
            fq_version_name,
        )
        existing_record_guid = existing_record[0]["attributes"].get("globalid")
        parcel_feature = [
            {"id": "{6E6D131E-32F4-4BAF-94E8-0F8D0122853F}", "layerId": "15"}
        ]

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Duplicate the parcels
            try:
                duplicate = parcel_fabric.duplicate(
                    parcels=parcel_feature,
                    record=existing_record_guid,
                    parcel_type=18,
                    parcel_subtype=-1,
                    repeat_count=5,
                    start_value=1000,
                    update_field="name",
                    increment_value=4,
                )
                self.assertTrue(
                    len(duplicate["serviceEdits"]) > 0,
                    "No edits returned from Duplicate.",
                )

                # Expecting 5 parcels starting from original parcel at 1000 up to 1016
                conveyance_div_lyr = pfutils.get_feature_layer(
                    self.parcel_fabric_flc, "ConveyanceDivision_PF"
                )
                increment_check = conveyance_div_lyr.query(
                    where="name IN  ('1000', '1004', '1008', '1012', '1016')",
                    out_fields=["name"],
                    gdb_version=fq_version_name,
                    return_geometry=False,
                )

                self.assertEqual(5, len(increment_check))
            except Exception as ex:
                self.fail(f"Duplicate failed: {str(ex)}")

    def test_duplicate_two_parcels_into_condiv_increment_field_async(self):
        fq_version_name = pfutils.create_version(self.vms)
        existing_record = pfutils.get_record_guid_by_name(
            self.gis,
            f"{self.service_urls['FeatureServer']}/1",
            "Record001",
            fq_version_name,
        )
        existing_record_guid = existing_record[0]["attributes"].get("globalid")
        parcel_features = self.load_feature_json()

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Duplicate the parcels
            try:
                duplicate_result = parcel_fabric.duplicate(
                    parcels=parcel_features,
                    record=existing_record_guid,
                    parcel_type=18,
                    parcel_subtype=-1,
                    repeat_count=2,
                    start_value=1000,
                    update_field="name",
                    increment_value=4,
                    future=True,
                )
                assert isinstance(duplicate_result, concurrent.futures.Future)
                result = duplicate_result.result()
                self.assertEqual(
                    "esriJobSucceeded",
                    result["status"],
                    f"Async job failed:\t{result['status']}",
                )

                # Expecting each parcel to be duplicate each with a 1000 and 1004 name
                conveyance_div_lyr = pfutils.get_feature_layer(
                    self.parcel_fabric_flc, "ConveyanceDivision_PF"
                )
                increment_check = conveyance_div_lyr.query(
                    where="name IN ('1000', '1004')",
                    out_fields=["name"],
                    gdb_version=fq_version_name,
                    return_geometry=False,
                )
                self.assertEqual(4, len(increment_check))

            except Exception as ex:
                self.fail(f"Duplicate failed: {str(ex)}")

    @classmethod
    def load_feature_json(self):
        parcels = [
            {"id": "{6E6D131E-32F4-4BAF-94E8-0F8D0122853F}", "layerId": "15"},
            {"id": "{13CD345B-7C4F-41C7-A22D-24E4C6670D85}", "layerId": "15"},
        ]
        return parcels

    @classmethod
    def tearDownClass(cls):
        pfutils.clean_up_versions(cls.vms)


if __name__ == "__main__":
    unittest.main(
        exit=False, failfast=True, buffer=False, catchbreak=False, verbosity=1
    )
