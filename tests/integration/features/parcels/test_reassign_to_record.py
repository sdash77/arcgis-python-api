import unittest
from arcgis.gis import GIS
from arcgis.features._parcel import ParcelFabricManager
from arcgis.features.layer import FeatureLayerCollection
from utils.decorators import integration_test, profiles
from . import parcel_fabric_utils as pfutils


@profiles.parcel_fabric
@integration_test
class TestReassignToRecord(unittest.TestCase):
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

        endpoints = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url + url for url in endpoints}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis
        )
        cls.vms = cls.parcel_fabric_flc.versions
        cls.records_service_url = f"{cls.service_urls['FeatureServer']}/1"

    def test_ReassignToRecordKeepSourceRecord(self):
        """
        Reassign parcels in a Record001 to Record002
        Check the parcel count switch in the records layer
        Check the CreatedByRecord value in the existing parcels
        Check the source record was not deleted.
        """
        fq_version_name = pfutils.create_version(self.vms)
        source_record = "{4B753DC5-AEDD-4703-AE56-B236EBB5DEFB}"
        target_record = "{D045AAA4-7308-4619-B2C7-1A905FDF07CE}"
        delete_source_record = False

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            result = parcel_fabric.reassign_features_to_record(
                source_record, target_record, delete_source_record
            )
            self.assertTrue(result, "Reassign to record failed.")

        records_lyr = pfutils.get_feature_layer(self.parcel_fabric_flc, "Records")
        target_record_query_result = records_lyr.query(
            where=f"GlobalID = '{target_record}' AND ParcelCount = 12",
            out_fields=["OBJECTID"],
            return_geometry=True,
            gdb_version=fq_version_name,
        )
        target_records = [
            s.as_dict.get("attributes") for s in target_record_query_result.features
        ]
        self.assertEqual(
            1, len(target_records), "Unexpected results from reassigned record query"
        )

        source_records_query_result = records_lyr.query(
            where=f"GlobalID = '{source_record}' AND ParcelCount = 0",
            out_fields=["OBJECTID"],
            return_geometry=True,
            gdb_version=fq_version_name,
        )
        source_records = [
            s.as_dict.get("attributes") for s in source_records_query_result.features
        ]
        self.assertEqual(
            1, len(source_records), "Unexpected results from source record query"
        )

        parcels_lyr = pfutils.get_feature_layer(self.parcel_fabric_flc, "Tax_PF")
        parcel_query_result = parcels_lyr.query(
            where=f"CreatedByRecord = '{target_record}'",
            out_fields=["OBJECTID"],
            return_geometry=True,
            gdb_version=fq_version_name,
        )
        parcels = [s.as_dict.get("attributes") for s in parcel_query_result.features]
        self.assertEqual(
            12, len(parcels), "Unexpected results from reassigned record query"
        )

    def test_ReassignToRecordDeleteSourceRecord(self):
        """
        Reassign parcels in a Record001 to Record002
        Check the parcel count switch in the records layer
        Check the CreatedByRecord value in the existing parcels
        Check the source record was deleted.
        """
        fq_version_name = pfutils.create_version(self.vms)
        source_record = "{4B753DC5-AEDD-4703-AE56-B236EBB5DEFB}"
        target_record = "{D045AAA4-7308-4619-B2C7-1A905FDF07CE}"
        delete_source_record = True

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            result = parcel_fabric.reassign_features_to_record(
                source_record, target_record, delete_source_record
            )
            self.assertTrue(result, "Reassign to record failed.")

        records_lyr = pfutils.get_feature_layer(self.parcel_fabric_flc, "Records")
        target_record_query_result = records_lyr.query(
            where=f"GlobalID = '{target_record}' AND ParcelCount = 12",
            out_fields=["OBJECTID"],
            return_geometry=True,
            gdb_version=fq_version_name,
        )
        target_records = [
            s.as_dict.get("attributes") for s in target_record_query_result.features
        ]
        self.assertEqual(
            1, len(target_records), "Unexpected results from reassigned record query"
        )

        source_records_query_result = records_lyr.query(
            where=f"GlobalID = '{source_record}'",
            out_fields=["OBJECTID"],
            return_geometry=True,
            gdb_version=fq_version_name,
        )
        source_records = [
            s.as_dict.get("attributes") for s in source_records_query_result.features
        ]
        self.assertEqual(
            0, len(source_records), "Unexpected results from source record query"
        )

        parcels_lyr = pfutils.get_feature_layer(self.parcel_fabric_flc, "Tax_PF")
        parcel_query_result = parcels_lyr.query(
            where=f"CreatedByRecord = '{target_record}'",
            out_fields=["OBJECTID"],
            return_geometry=True,
            gdb_version=fq_version_name,
        )
        parcels = [s.as_dict.get("attributes") for s in parcel_query_result.features]
        self.assertEqual(
            12, len(parcels), "Unexpected results from reassigned record query"
        )

    @classmethod
    def tearDownClass(cls):
        pfutils.clean_up_versions(cls.vms)


if __name__ == "__main__":
    unittest.main()
