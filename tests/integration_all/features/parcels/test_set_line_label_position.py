import unittest
import time
import concurrent.futures
from arcgis.gis import GIS
from arcgis.features.layer import FeatureLayerCollection
from arcgis.features._parcel import ParcelFabricManager
from utils.decorators import integration_test
from . import parcel_fabric_utils as pfutils


@integration_test
class TestSetLineLabelPosition(unittest.TestCase):
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
            "https://dev0016752.esri.com/server/rest/services/Redlands/"
        )
        cls.gis = GIS("https://dev0016752.esri.com/portal/", "admin", "esri.agp", verify_cert=False)
        endpoints = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url + url for url in endpoints}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis
        )
        cls.vms = cls.parcel_fabric_flc.versions

    def test_set_label_position_sync(self):
        fq_version_name = pfutils.create_version(self.vms, f"api-{int(time.time())}")
        source_parcels = [
            {"id": "{4DC4FC70-7597-4A3C-81E1-7E245B7126F2}", "layerId": "14"},
            {"id": "{C4FE6C47-5B7E-440B-AA77-9B58D1A09C53}", "layerId": "14"},
            {"id": "{EB0B94F5-3EF2-4B6B-87DE-3B4537AF62DA}", "layerId": "14"},
            {"id": "{6E2E5F1B-0754-44A9-A745-F27EEA2110D0}", "layerId": "14"},
            {"id": "{648E1F32-C742-480B-8224-0495ECD0E578}", "layerId": "14"},
            {"id": "{F1578D10-9598-4B44-8DF2-1DF19B1D2DE1}", "layerId": "14"},
            {"id": "{E0670BA3-A11A-43E6-A4A4-BD07394042EB}", "layerId": "14"},
            {"id": "{91F23557-4411-4E76-B3A5-8DB84EE2768A}", "layerId": "14"},
        ]

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )

            try:
                res = parcel_fabric.set_line_label_position(
                    parcel_line_features=source_parcels
                )
                self.assertTrue(res["success"])
                self.assertEqual(
                    2, len(res["serviceEdits"][0]["editedFeatures"]["updates"][0])
                )
            except Exception as ex:
                print(ex)

    def test_set_label_position_async(self):
        fq_version_name = pfutils.create_version(self.vms, f"api-{int(time.time())}")
        source_parcels = [
            {"id": "{4DC4FC70-7597-4A3C-81E1-7E245B7126F2}", "layerId": "14"},
            {"id": "{C4FE6C47-5B7E-440B-AA77-9B58D1A09C53}", "layerId": "14"},
            {"id": "{EB0B94F5-3EF2-4B6B-87DE-3B4537AF62DA}", "layerId": "14"},
            {"id": "{6E2E5F1B-0754-44A9-A745-F27EEA2110D0}", "layerId": "14"},
            {"id": "{648E1F32-C742-480B-8224-0495ECD0E578}", "layerId": "14"},
            {"id": "{F1578D10-9598-4B44-8DF2-1DF19B1D2DE1}", "layerId": "14"},
            {"id": "{E0670BA3-A11A-43E6-A4A4-BD07394042EB}", "layerId": "14"},
            {"id": "{91F23557-4411-4E76-B3A5-8DB84EE2768A}", "layerId": "14"},
        ]

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )

            try:
                result = parcel_fabric.set_line_label_position(
                    parcel_line_features=source_parcels, future=True
                )
                assert isinstance(result, concurrent.futures.Future)
                result = result.result()
                self.assertEqual(
                    "esriJobSucceeded",
                    result["status"],
                    f"Async job failed:\t{result['messages']}",
                )

                if not result["success"]:
                    self.fail(
                        f"An error occurred setting line labels: {result['status']}"
                    )

                # Check that one feature is now retired
                updated_lines = feature_utils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=14,
                    gis=self.gis,
                    where=f"OBJECTID = 1223",
                    out_fields=["LabelPosition"],
                    version_name=fq_version_name,
                ).to_dict()

                label_positon = updated_lines.get("features")[0]
                label_position = label_positon.get("attributes")["LabelPosition"]
                self.assertEqual(
                    3,
                    label_position,
                    f"Unexpected LabelPosition value. Expected 3, got {label_positon}",
                )
            except Exception as ex:
                print(ex)


if __name__ == "__main__":
    unittest.main()
