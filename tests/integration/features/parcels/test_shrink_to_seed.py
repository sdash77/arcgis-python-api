import unittest
import time
import concurrent.futures
from arcgis.gis import GIS
from arcgis.features.layer import FeatureLayerCollection, FeatureLayer
from arcgis.features._parcel import ParcelFabricManager
from utils.decorators import integration_test, profiles
from . import parcel_fabric_utils as pfutils


@profiles.parcel_fabric
@integration_test
class TestShrinkToSeed(unittest.TestCase):
    """Tests the Shrink To Seed function from the parcel fabric SOE"""

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
            "https://dev0016752.esri.com/server/rest/services/WashingtonCountyLSA/"
        )
        endpoints = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url + url for url in endpoints}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis
        )
        cls.vms = cls.parcel_fabric_flc.versions
        cls.tax_parcel_layer = [
            l for l in cls.parcel_fabric_flc.layers if l.properties.id == 15
        ][0]
        assert isinstance(
            cls.tax_parcel_layer, FeatureLayer
        ), "Failed to access tax parcels"

    def test_shrink_to_seed_sync(self):
        fq_version_name = self.vms.create(f"api-{int(time.time())}")["versionInfo"][
            "versionName"
        ]
        version_parts = fq_version_name.split(".")
        source_parcels = [
            {"id": "{50C7CB87-F407-473A-9F0B-462C2DCFF621}", "layerId": "15"},
            {"id": "{5909A555-0ED3-47BC-B366-3BAF65BEFED9}", "layerId": "15"},
            {"id": "{EC321A62-1BF4-4D80-9F7B-C402EE79E629}", "layerId": "15"},
            {"id": "{077C36CB-0E7B-4AB3-BA6F-7EF4F2C166D9}", "layerId": "15"},
            {"id": "{B00EF83E-DDAB-4E16-B872-D3663578F944}", "layerId": "15"},
        ]

        with self.vms.get_by_name(
            version_parts[0], version_parts[1], "read"
        ) as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )

            try:
                res = parcel_fabric.shrink_to_seed(
                    parcel_features=source_parcels, future=False
                )
                self.assertTrue(res["success"])
                self.assertEqual(
                    2, len(res["serviceEdits"][0]["editedFeatures"]["updates"][0])
                )
                is_seed = self.tax_parcel_layer.query(
                    "IsSeed = 1", gdb_version=fq_version_name
                )
                self.assertEqual(
                    5,
                    len(is_seed),
                    f"Incorrect count of seed parcels. Got: {len(is_seed)}",
                )
            except Exception as ex:
                self.fail(ex)

    def test_shrink_to_seed_include_lines_sync(self):
        fq_version_name = self.vms.create(f"api-{int(time.time())}")["versionInfo"][
            "versionName"
        ]
        version_parts = fq_version_name.split(".")
        source_parcels = [
            {"id": "{81A62E43-F5C2-4AD9-B134-212E696EDB0F}", "layerId": "14"},
            {"id": "{16375D26-885D-4F6C-83E2-90C41064C57E}", "layerId": "14"},
            {"id": "{22A4E6DC-1D3F-4FDE-A5B8-565BAE9661D6}", "layerId": "14"},
            {"id": "{9755F9F1-273C-4719-9328-1CBF4C5693AB}", "layerId": "14"},
            {"id": "{595D0C26-55B2-4527-94A4-D395C727FFB3}", "layerId": "14"},
            {"id": "{D500E389-0B0C-4C40-8FE4-422E9D63D6B4}", "layerId": "14"},
            {"id": "{9DAE5002-D4BB-4D7D-A8C1-96A39A60AA2F}", "layerId": "14"},
            {"id": "{50C7CB87-F407-473A-9F0B-462C2DCFF621}", "layerId": "15"},
            {"id": "{5909A555-0ED3-47BC-B366-3BAF65BEFED9}", "layerId": "15"},
            {"id": "{EC321A62-1BF4-4D80-9F7B-C402EE79E629}", "layerId": "15"},
            {"id": "{077C36CB-0E7B-4AB3-BA6F-7EF4F2C166D9}", "layerId": "15"},
            {"id": "{B00EF83E-DDAB-4E16-B872-D3663578F944}", "layerId": "15"},
        ]
        with self.vms.get_by_name(
            version_parts[0], version_parts[1], "read"
        ) as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )

            try:
                res = parcel_fabric.shrink_to_seed(
                    parcel_features=source_parcels, future=False
                )
                self.assertTrue(res["success"])
                self.assertEqual(
                    2, len(res["serviceEdits"][0]["editedFeatures"]["updates"][0])
                )
                is_seed = self.tax_parcel_layer.query(
                    "IsSeed = 1", gdb_version=fq_version_name
                )
                self.assertEqual(
                    5,
                    len(is_seed),
                    f"Incorrect count of seed parcels. Got: {len(is_seed)}",
                )
            except Exception as ex:
                self.fail(ex)

    def test_shrink_to_seed_async(self):
        fq_version_name = self.vms.create(f"api-{int(time.time())}")["versionInfo"][
            "versionName"
        ]
        version_parts = fq_version_name.split(".")
        source_parcels = [
            {"id": "{50C7CB87-F407-473A-9F0B-462C2DCFF621}", "layerId": "15"},
            {"id": "{5909A555-0ED3-47BC-B366-3BAF65BEFED9}", "layerId": "15"},
            {"id": "{EC321A62-1BF4-4D80-9F7B-C402EE79E629}", "layerId": "15"},
            {"id": "{077C36CB-0E7B-4AB3-BA6F-7EF4F2C166D9}", "layerId": "15"},
            {"id": "{B00EF83E-DDAB-4E16-B872-D3663578F944}", "layerId": "15"},
        ]

        with self.vms.get_by_name(
            version_parts[0], version_parts[1], "read"
        ) as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )

            try:
                res = parcel_fabric.shrink_to_seed(
                    parcel_features=source_parcels, future=True
                )
                assert isinstance(res, concurrent.futures.Future)
                result = res.result()
                self.assertEqual(
                    "esriJobSucceeded",
                    result["status"],
                    f"Async job failed:\t{result['progressMessage']}",
                )

                if not result["success"]:
                    self.fail(
                        f"An error occurred shrinking to seed: {result['status']}"
                    )

                is_seed = self.tax_parcel_layer.query(
                    "IsSeed = 1", gdb_version=fq_version_name
                )
                self.assertEqual(
                    5,
                    len(is_seed),
                    f"Incorrect count of seed parcels. Got: {len(is_seed)}",
                )
            except Exception as ex:
                self.fail(ex)

    @classmethod
    def tearDownClass(cls):
        pfutils.clean_up_versions(cls.vms)


if __name__ == "__main__":
    unittest.main()
