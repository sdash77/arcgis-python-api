import unittest
from arcgis.gis import GIS
from arcgis.features._parcel import ParcelFabricManager
from arcgis.features.layer import FeatureLayerCollection
from utils.decorators import integration_test
from . import parcel_fabric_utils as pfutils


@integration_test
class TestDeleteParcels(unittest.TestCase):
    """Delete parcels"""

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
        cls.records_service_url = f"{cls.service_urls['FeatureServer']}/1"

    def test_delete_multiple_parcels(self):
        fq_version_name = pfutils.create_version(self.vms)
        parcel_features = [
            {"id": "{509D74F0-3309-4D86-9BCE-C231E96D822E}", "layerId": 15},
            {"id": "{B35D8021-28DA-4D8A-B352-57E4C049089B}", "layerId": 15},
        ]

        with self.vms.get(fq_version_name, "read") as version:
            self.parcelFabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )

            delete_parcels = self.parcelFabric.delete(parcels=parcel_features)
            edits = delete_parcels.get("serviceEdits")
            self.assertEqual(4, len(edits), "Missing layer edits")
            records_edits = [e["editedFeatures"] for e in edits if e["id"] == 1][0].get(
                "updates"
            )
            parcels_edits = [e["editedFeatures"] for e in edits if e["id"] == 15][
                0
            ].get("deletes")
            parcel_lines_edits = [e["editedFeatures"] for e in edits if e["id"] == 14][
                0
            ].get("deletes")
            self.assertIsNotNone(records_edits, "No Records edits found")
            self.assertIsNotNone(parcels_edits, "No Parcels edits found")
            self.assertIsNotNone(parcel_lines_edits, "No Parcel Lines edits found")

    def test_delete_multiple_parcels_wrong_layerid(self):
        fq_version_name = pfutils.create_version(self.vms)
        parcel_features = [
            {"id": "{BEC4C8B2-C381-4E5C-95A3-DCE12549EBF1}", "layerId": 99},
            {"id": "{03255D2E-4306-40F0-882F-9991735AAF64}", "layerId": 99},
        ]

        with self.vms.get(fq_version_name, "read") as version:
            self.parcelFabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            with self.assertRaises(Exception) as ex:
                delete_parcels = self.parcelFabric.delete(parcels=parcel_features)
                error_str = "Invalid function arguments"
                self.assertTrue(error_str in str(ex.exception))

                edits = delete_parcels.get("serviceEdits")
                self.assertEqual(None, edits, "Edits were found after delete.")

    @classmethod
    def tearDownClass(cls):
        pfutils.clean_up_versions(cls.vms)


if __name__ == "__main__":
    unittest.main()
