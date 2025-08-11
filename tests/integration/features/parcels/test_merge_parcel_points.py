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
class TestMergeParcelPoints(unittest.TestCase):
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
            "https://dev0016752.esri.com/server/rest/services/MergePointsREST/"
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

    def test_merge_points_all_args_sync(self):
        fq_version_name = self.vms.create(f"api-{int(time.time())}")["versionInfo"][
            "versionName"
        ]
        version_parts = fq_version_name.split(".")
        input_points = [
            "{BE28A958-41E1-4F68-82E4-6CC99ADCBE9E}",
            "{975A5F00-EB74-40DB-A347-7B33A4EC0AD5}",
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
            result = parcel_fabric.merge_parcel_points(
                input_parcel_points=input_points,
                preserve_point_guid="{975A5F00-EB74-40DB-A347-7B33A4EC0AD5}",
                location_point_guid="{975A5F00-EB74-40DB-A347-7B33A4EC0AD5}",
                update_features=True,
                remove_lines=True,
                attribute_overrides={
                    "type": "PropertySet",
                    "propertySetItems": [
                        "CreatedByRecord",
                        "{7A62662C-AB96-4056-B007-9EBCEEC957D9}",
                        "IsFixed",
                        0,
                        "AdjustmentConstraint",
                        1,
                        "Preserve",
                        0,
                        "Name",
                        "name_updated_by_test",
                    ],
                },
                future=False,
            )
            self.assertTrue(result.get("success"))
            service_edits = result.get("serviceEdits")
            line_edits = [e for e in service_edits if e["id"] == 18][0].get(
                "editedFeatures"
            )
            line_updates = line_edits.get("updates")
            self.assertEqual(
                3,
                len(line_updates),
                f"Incorrect quantity of line edits. Got {len(line_updates)}",
            )

            points_fl = [
                l
                for l in self.parcel_fabric_flc.layers
                if l.properties.name == "Points"
            ][0]
            points_query = points_fl.query(
                where="Name='name_updated_by_test'", gdb_version=fq_version_name
            )
            self.assertIsNotNone(points_query.features, "Empty points query result")
            rows = points_query.features
            self.assertEqual(
                1,
                len(rows),
                f"Incorrect quantity of features. Got {len(rows)}",
            )

    def test_merge_points_all_args_async(self):
        fq_version_name = self.vms.create(f"api-{int(time.time())}")["versionInfo"][
            "versionName"
        ]
        version_parts = fq_version_name.split(".")
        input_points = [
            "{BE28A958-41E1-4F68-82E4-6CC99ADCBE9E}",
            "{975A5F00-EB74-40DB-A347-7B33A4EC0AD5}",
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
            result = parcel_fabric.merge_parcel_points(
                input_parcel_points=input_points,
                preserve_point_guid="{975A5F00-EB74-40DB-A347-7B33A4EC0AD5}",
                location_point_guid="{975A5F00-EB74-40DB-A347-7B33A4EC0AD5}",
                update_features=True,
                remove_lines=True,
                attribute_overrides={
                    "type": "PropertySet",
                    "propertySetItems": [
                        "CreatedByRecord",
                        "{7A62662C-AB96-4056-B007-9EBCEEC957D9}",
                        "IsFixed",
                        0,
                        "AdjustmentConstraint",
                        1,
                        "Preserve",
                        0,
                        "Name",
                        "name_updated_by_test",
                    ],
                },
                future=True,
            )
            assert isinstance(result, concurrent.futures.Future)
            result = result.result()
            self.assertEqual(
                "esriJobSucceeded",
                result["status"],
                f"Async job failed:\t{result['progressMessage']}",
            )
            points_fl = [
                l
                for l in self.parcel_fabric_flc.layers
                if l.properties.name == "Points"
            ][0]
            points_query = points_fl.query(
                where="Name='name_updated_by_test'", gdb_version=fq_version_name
            )
            self.assertIsNotNone(points_query.features, "Empty points query result")
            rows = points_query.features
            self.assertEqual(
                1,
                len(rows),
                f"Incorrect quantity of features. Got {len(rows)}",
            )

    @classmethod
    def tearDownClass(cls):
        pfutils.clean_up_versions(cls.vms)


if __name__ == "__main__":
    unittest.main()
