import unittest
import time
import concurrent.futures
from arcgis.gis import GIS
from arcgis.features.layer import FeatureLayer, FeatureLayerCollection
from arcgis.features._parcel import ParcelFabricManager
from utils.decorators import integration_test, profiles
from . import parcel_fabric_utils as pfutils


@profiles.parcel_fabric
@integration_test
class TestTransferParcels(unittest.TestCase):
    """Tests the Transfer Parcel function from the parcel fabric SOE"""

    gis = None
    vms = None
    services = None
    service_urls = {}
    base_server_url = None
    parcel_fabric_flc = None

    @classmethod
    def setUpClass(cls):
        # Create Python API GIS object and prepare REST service URL strings
        cls.base_server_url = (
            "https://dev0016752.esri.com/server/rest/services/HCAD_Subset/"
        )

        endpoints = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url + url for url in endpoints}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis
        )
        cls.vms = cls.parcel_fabric_flc.versions

    def test_scenario_1(self):
        fq_version_name = pfutils.create_version(self.vms, f"api-{int(time.time())}")
        transfer_parcel = {
            "id": "{D664B654-D8F2-453C-966F-6FA66E1AE2E2}",
            "layerId": "24",
        }
        source_parcels = [
            {"id": "{8233045B-A337-4087-957A-4F8A4814FF09}", "layerId": "15"},
            {"id": "{EC850938-01F4-48C6-B7DB-16EFB0B544BC}", "layerId": "15"},
            {"id": "{BCF8B086-B5DB-472A-89AA-6A3AF54C75BD}", "layerId": "15"},
        ]
        target_parcels = [
            {"id": "{449572F3-C2E1-405D-B642-4CFA90C10C46}", "layerId": "21"}
        ]
        parcel_record = "{89E0F2EE-9788-4008-9CD4-1F02ABDCD49F}"
        area_unit = 109405

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )

            try:
                res = parcel_fabric.transfer_parcel(
                    transfer_parcel_feature=transfer_parcel,
                    target_parcel_features=target_parcels,
                    record=parcel_record,
                    default_area_unit=109405,
                    source_parcel_features=source_parcels,
                )
                self.assertTrue(res["success"])
            except Exception as ex:
                print(ex)

            # Check that one feature is now retired
            lot_fl = FeatureLayer(f"{self.service_urls['FeatureServer']}/21", self.gis)
            retired_features = lot_fl.query(
                where=f"CreatedByRecord = '{parcel_record}'",
                out_fields=["GlobalID"],
                gdb_version=fq_version_name,
            ).to_dict()
            self.assertEqual(
                1,
                len(retired_features["features"]),
                "Did not find the transferred parcel.",
            )

            # Check that one feature is now retired
            lot_lines = FeatureLayer(
                f"{self.service_urls['FeatureServer']}/20", self.gis
            )
            retired_lines = lot_lines.query(
                where=f"RetiredByRecord = '{parcel_record}'",
                out_fields=["GlobalID"],
                gdb_version=fq_version_name,
            ).to_dict()
            self.assertEqual(
                3,
                len(retired_lines["features"]),
                "Did not find a retired line.",
            )

    @classmethod
    def tearDownClass(cls):
        pfutils.clean_up_versions(cls.vms)


if __name__ == "__main__":
    unittest.main()
