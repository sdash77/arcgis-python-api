import concurrent.futures
import unittest
import concurrent.futures
from arcgis.gis import GIS
from arcgis.features.layer import FeatureLayer, FeatureLayerCollection
from arcgis.features._parcel import ParcelFabricManager
from utils.decorators import integration_test, profiles
from . import parcel_fabric_utils as pfutils


@profiles.parcel_fabric
@integration_test
class TestDivideParcels(unittest.TestCase):
    """Tests the Divide function from the parcel fabric SOE"""

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
            "https://dev0016752.esri.com/server/rest/services/Divide1091/"
        )

        endpoints = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url + url for url in endpoints}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis
        )
        cls.vms = cls.parcel_fabric_flc.versions

        cls.tax_lyr_info = pfutils.basic_lyr_info(cls.parcel_fabric_flc, "Tax_Div")[0]
        cls.tax_lyr_id = cls.tax_lyr_info.lyr_id

        cls.tax_line_info = pfutils.basic_lyr_info(
            cls.parcel_fabric_flc, "Tax_Div_Lines"
        )[0]
        cls.tax_line_id = cls.tax_line_info.lyr_id

    def test_divide_proportional_area_no_dist_remainder(self):
        fq_version_name = pfutils.create_version(self.vms, "api-divide_prop_area")
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "ProportionalArea"
        number_of_parts = 4
        divide_part_area_or_width = 0
        divide_line_bearing = 180
        divide_left_side = False
        divide_distribute_remainder = False
        default_area_unit = 109405

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=None,
                    default_area_unit=default_area_unit,
                )
                self.assertTrue(divide, "Divide failed.")
                # Check for correct qty of inserts and updates to polygons
                divide_result = next(x for x in divide["serviceEdits"] if x["id"] == 15)
                adds = divide_result["editedFeatures"]["adds"]
                updates = divide_result["editedFeatures"]["updates"]
                self.assertEqual(4, len(adds), "Incorrect number of polygon adds")
                self.assertEqual(1, len(updates), "Incorrect number of polygon updates")
                # Check that one feature is now retired
                retired_features = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="RetiredByRecord IS NOT NULL",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    1,
                    len(retired_features["features"]),
                    "Did not find a retired parcel.",
                )
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_divide_proportional_area_no_dist_remainder_timed(self):
        fq_version_name = pfutils.create_version(self.vms)
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "ProportionalArea"
        number_of_parts = 4
        divide_part_area_or_width = 0
        divide_line_bearing = 179.882
        divide_left_side = False
        divide_distribute_remainder = False
        default_area_unit = 109405

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=None,
                    default_area_unit=default_area_unit,
                )
                self.assertTrue(divide, "Divide failed.")
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_proportional_area_check_defaults(self):
        fq_version_name = pfutils.create_version(self.vms)
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "ProportionalArea"
        number_of_parts = 4
        divide_line_bearing = 180
        divide_part_area_or_width = None
        divide_left_side = None
        divide_distribute_remainder = None
        default_area_unit = 109405

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=None,
                    default_area_unit=default_area_unit,
                )
                self.assertTrue(divide, "Divide failed.")
                # Check for correct qty of inserts and updates to polygons
                divide_result = next(x for x in divide["serviceEdits"] if x["id"] == 15)
                adds = divide_result["editedFeatures"]["adds"]
                updates = divide_result["editedFeatures"]["updates"]
                self.assertEqual(4, len(adds), "Incorrect number of polygon adds")
                self.assertEqual(1, len(updates), "Incorrect number of polygon updates")
                # Check that one feature is now retired
                retired_features = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="RetiredByRecord IS NOT NULL",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    1,
                    len(retired_features["features"]),
                    "Did not find a retired parcel.",
                )
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_divide_equal_area_no_dist_remainder(self):
        fq_version_name = pfutils.create_version(self.vms)
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "EqualArea"
        number_of_parts = 4
        divide_part_area_or_width = 2010
        divide_line_bearing = 360
        divide_left_side = False
        divide_distribute_remainder = False
        default_area_unit = 109405

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=None,
                    default_area_unit=default_area_unit,
                )
                self.assertTrue(divide, "Divide failed.")
                # Check for correct qty of inserts and updates to polygons
                divide_result = next(x for x in divide["serviceEdits"] if x["id"] == 15)
                adds = divide_result["editedFeatures"]["adds"]
                updates = divide_result["editedFeatures"]["updates"]
                self.assertEqual(5, len(adds), "Incorrect number of polygon adds")
                self.assertEqual(1, len(updates), "Incorrect number of polygon updates")
                # Check that one feature is now retired
                retired_features = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="RetiredByRecord IS NOT NULL",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    1,
                    len(retired_features["features"]),
                    "Did not find a retired parcel.",
                )
                remainder_feature = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="Shape__Area < 50",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    1,
                    len(retired_features["features"]),
                    "Did not find a small (< 50 sqft) parcel.",
                )
                self.assertIsNotNone(
                    remainder_feature, "Error creating remainder feature"
                )
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_equal_area_dist_remainder_left_side_true(self):
        fq_version_name = pfutils.create_version(self.vms)
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "EqualArea"
        number_of_parts = 4
        divide_part_area_or_width = 2010
        divide_line_bearing = 360
        divide_left_side = True
        divide_distribute_remainder = True
        default_area_unit = 109405

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=None,
                    default_area_unit=default_area_unit,
                )
                self.assertTrue(divide, "Divide failed.")
                # Check for correct qty of inserts and updates to polygons
                divide_result = next(x for x in divide["serviceEdits"] if x["id"] == 15)
                adds = divide_result["editedFeatures"]["adds"]
                updates = divide_result["editedFeatures"]["updates"]
                self.assertEqual(4, len(adds), "Incorrect number of polygon adds")
                self.assertEqual(1, len(updates), "Incorrect number of polygon updates")
                # Check that one feature is now retired
                retired_features = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="RetiredByRecord IS NOT NULL",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    1,
                    len(retired_features["features"]),
                    "Did not find a retired parcel.",
                )
                remainder_feature = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="Shape__Area < 50",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    0,
                    len(remainder_feature["features"]),
                    "Found a sliver (< 50 sqft) parcel.",
                )
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_equal_area_dist_remainder(self):
        fq_version_name = pfutils.create_version(self.vms, "api-divide_equal_area")
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "EqualArea"
        number_of_parts = 2
        divide_part_area_or_width = 4020
        divide_line_bearing = 360
        divide_left_side = True
        divide_distribute_remainder = True
        default_area_unit = 109405

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=None,
                    default_area_unit=default_area_unit,
                )
                self.assertTrue(divide, "Divide failed.")
                # Check for correct qty of inserts and updates to polygons
                divide_result = next(x for x in divide["serviceEdits"] if x["id"] == 15)
                adds = divide_result["editedFeatures"]["adds"]
                updates = divide_result["editedFeatures"]["updates"]
                self.assertEqual(2, len(adds), "Incorrect number of polygon adds")
                self.assertEqual(1, len(updates), "Incorrect number of polygon updates")
                # Check that one feature is now retired
                retired_features = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="RetiredByRecord IS NOT NULL",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    1,
                    len(retired_features["features"]),
                    "Did not find a retired parcel.",
                )
                remainder_feature = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="Shape__Area < 50",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    0,
                    len(remainder_feature["features"]),
                    "Found a sliver (< 50 sqft) parcel.",
                )
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_equal_area_dist_remainder_square(self):
        fq_version_name = pfutils.create_version(self.vms)
        divide_parcel_guid = "{6A072F92-2345-40B0-9F21-BE4BFBC7E2B6}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "EqualArea"
        number_of_parts = 2
        divide_part_area_or_width = 4999.99
        divide_line_bearing = 360
        divide_left_side = True
        divide_distribute_remainder = True
        default_area_unit = 109405

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=None,
                    default_area_unit=default_area_unit,
                )
                self.assertTrue(divide, "Divide failed.")
                # Check for correct qty of inserts and updates to polygons
                divide_result = next(x for x in divide["serviceEdits"] if x["id"] == 15)
                adds = divide_result["editedFeatures"]["adds"]
                updates = divide_result["editedFeatures"]["updates"]
                self.assertEqual(2, len(adds), "Incorrect number of polygon adds")
                self.assertEqual(1, len(updates), "Incorrect number of polygon updates")
                self.assertAlmostEqual(
                    5005,
                    adds[0]["attributes"]["Shape__Area"],
                    1,
                    "Incorrect polygon area",
                )
                self.assertAlmostEqual(
                    5005,
                    adds[0]["attributes"]["Shape__Area"],
                    1,
                    "Incorrect polygon area",
                )
                self.assertEqual(
                    adds[1]["attributes"]["Shape__Area"],
                    adds[0]["attributes"]["Shape__Area"],
                    "Areas are not equal",
                )
                # Check that one feature is now retired
                retired_features = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="RetiredByRecord IS NOT NULL",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    1,
                    len(retired_features["features"]),
                    "Did not find a retired parcel.",
                )
                remainder_feature = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="Shape__Area < 50",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    0,
                    len(remainder_feature["features"]),
                    "Found a sliver (< 50 sqft) parcel.",
                )
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_equal_area_dist_remainder_left_side_false(self):
        fq_version_name = pfutils.create_version(self.vms)
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "EqualArea"
        number_of_parts = 4
        divide_part_area_or_width = 2023  # 2023.9434823110323
        divide_line_bearing = 11  # 8.9839430623222967
        divide_left_side = False
        divide_distribute_remainder = True
        default_area_unit = 109405

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=None,
                    default_area_unit=default_area_unit,
                )
                self.assertTrue(divide, "Divide failed.")
                # Check for correct qty of inserts and updates to polygons
                divide_result = next(x for x in divide["serviceEdits"] if x["id"] == 15)
                adds = divide_result["editedFeatures"]["adds"]
                updates = divide_result["editedFeatures"]["updates"]
                self.assertEqual(4, len(adds), "Incorrect number of polygon adds")
                self.assertEqual(1, len(updates), "Incorrect number of polygon updates")
                # Check that one feature is now retired
                retired_features = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="RetiredByRecord IS NOT NULL",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    1,
                    len(retired_features["features"]),
                    "Did not find a retired parcel.",
                )
                remainder_feature = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="Shape__Area < 50",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    0,
                    len(remainder_feature["features"]),
                    "Found a sliver (< 50 sqft) parcel.",
                )
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_equal_area_dist_remainder_cogo_line_bearing(self):
        fq_version_name = pfutils.create_version(self.vms)
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "EqualArea"
        number_of_parts = 4
        divide_part_area_or_width = 2023  # 2023.9434823110323
        divide_line_bearing = 11  # 8.9839430623222967
        divide_left_side = False
        divide_distribute_remainder = True
        default_area_unit = 109405
        divide_cogo_line_bearing = divide_line_bearing
        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=divide_cogo_line_bearing,
                    default_area_unit=default_area_unit,
                )
                self.assertTrue(divide, "Divide failed.")
                # Check for correct qty of inserts and updates to polygons
                divide_result = next(x for x in divide["serviceEdits"] if x["id"] == 15)
                adds = divide_result["editedFeatures"]["adds"]
                updates = divide_result["editedFeatures"]["updates"]
                self.assertEqual(4, len(adds), "Incorrect number of polygon adds")
                self.assertEqual(1, len(updates), "Incorrect number of polygon updates")
                # Check that one feature is now retired
                retired_features = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="RetiredByRecord IS NOT NULL",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    1,
                    len(retired_features["features"]),
                    "Did not find a retired parcel.",
                )
                remainder_feature = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="Shape__Area < 50",
                    out_fields=["objectid, Shape__Area"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    0,
                    len(remainder_feature["features"]),
                    "Found a sliver (< 50 sqft) parcel.",
                )
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_equal_width_merge_remainder_left_side_true(self):
        fq_version_name = pfutils.create_version(self.vms)
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "EqualWidth"
        number_of_parts = 10
        divide_part_area_or_width = 10
        divide_line_bearing = 359.9
        divide_left_side = True
        divide_distribute_remainder = True
        default_area_unit = 109405
        divide_cogo_line_bearing = None

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=divide_cogo_line_bearing,
                    default_area_unit=default_area_unit,
                )
                self.assertTrue(divide, "Divide failed.")
                # Check for correct qty of inserts and updates to polygons
                divide_result = next(x for x in divide["serviceEdits"] if x["id"] == 15)
                adds = divide_result["editedFeatures"]["adds"]
                updates = divide_result["editedFeatures"]["updates"]
                self.assertEqual(
                    10,
                    len(adds),
                    f"Incorrect number of polygon adds. Expected 10, got {len(adds)}",
                )
                self.assertEqual(1, len(updates), "Incorrect number of polygon updates")
                # Check that one feature is now retired
                retired_features = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="RetiredByRecord IS NOT NULL",
                    out_fields=["objectid"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    1,
                    len(retired_features["features"]),
                    "Did not find a retired parcel.",
                )
                remainder_feature = pfutils.query_service(
                    url=self.service_urls["FeatureServer"],
                    fl_id=15,
                    gis=self.gis,
                    where="objectid > 500 AND Shape__Area BETWEEN 1347 AND 1349",
                    out_fields=["objectid", "Shape__Area"],
                    version_name=fq_version_name,
                ).to_dict()
                self.assertEqual(
                    1,
                    len(remainder_feature["features"]),
                    "Did not find large remainder parcel.",
                )
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_equal_width_merge_remainder_left_side_timed(self):
        fq_version_name = pfutils.create_version(self.vms, "api-divide_equal_width")
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "EqualWidth"
        number_of_parts = 10
        divide_part_area_or_width = 10
        divide_line_bearing = 360
        divide_left_side = True
        divide_distribute_remainder = True
        default_area_unit = 109405
        divide_cogo_line_bearing = None

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=divide_cogo_line_bearing,
                    default_area_unit=default_area_unit,
                )
                self.assertTrue(divide, "Divide failed.")
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_equal_width_merge_remainder_left_side_async(self):
        fq_version_name = pfutils.create_version(self.vms, "api-divide_equal_width")
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "EqualWidth"
        number_of_parts = 10
        divide_part_area_or_width = 10
        divide_line_bearing = 360
        divide_left_side = True
        divide_distribute_remainder = True
        default_area_unit = 109405
        divide_cogo_line_bearing = None
        future = True

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide_result = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=divide_cogo_line_bearing,
                    default_area_unit=default_area_unit,
                    future=future,
                )
                assert isinstance(divide_result, concurrent.futures.Future)
                result = divide_result.result()
                self.assertEqual(
                    "esriJobSucceeded",
                    result["status"],
                    f"Async job failed:\t{result['status']}",
                )
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_equal_width_merge_remainder_include_lines(self):
        fq_version_name = pfutils.create_version(self.vms)
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = self.tax_lyr_id
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "EqualWidth"
        number_of_parts = 10
        divide_part_area_or_width = 10
        divide_line_bearing = 359.9
        divide_left_side = True
        divide_distribute_remainder = True
        default_area_unit = 109405
        divide_cogo_line_bearing = None
        divide_associated_lines = True

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            try:
                divide = parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=divide_cogo_line_bearing,
                    divide_associated_lines=divide_associated_lines,
                    default_area_unit=default_area_unit,
                )
                self.assertTrue(divide, "Divide failed.")
                # Check for correct qty of inserts and updates to polygons
                divide_result = next(
                    x for x in divide["serviceEdits"] if x["id"] == self.tax_lyr_id
                )
                divide_line_result = next(
                    x for x in divide["serviceEdits"] if x["id"] == self.tax_line_id
                )
                adds = divide_result["editedFeatures"]["adds"]
                updates = divide_result["editedFeatures"]["updates"]
                line_adds = divide_line_result["editedFeatures"]["adds"]
                line_updates = divide_line_result["editedFeatures"]["updates"]
                self.assertEqual(
                    10,
                    len(adds),
                    f"Incorrect number of polygon adds. Expected 10, got {len(adds)}",
                )
                self.assertEqual(
                    29,
                    len(line_adds),
                    f"Incorrect number of line edits, got {len(line_adds)}",
                )
                self.assertEqual(1, len(updates), "Incorrect number of polygon updates")
                self.assertEqual(
                    2, len(line_updates), "Incorrect number of line updates"
                )
                # Check that one feature is now retired
                tax_fl = FeatureLayer(
                    f"{self.service_urls['FeatureServer']}/{self.tax_lyr_id}"
                )
                tax_line_fl = FeatureLayer(
                    f"{self.service_urls['FeatureServer']}/{self.tax_line_id}"
                )
                retired_features = tax_fl.query(
                    where="RetiredByRecord IS NOT NULL",
                    gdb_version=fq_version_name,
                    out_fields=["OBJECTID"],
                ).to_dict()
                self.assertEqual(
                    1,
                    len(retired_features["features"]),
                    "Did not find a retired parcel.",
                )
                retired_line_features = tax_line_fl.query(
                    url=self.service_urls["FeatureServer"],
                    where="RetiredByRecord IS NOT NULL",
                    gdb_version=fq_version_name,
                    out_fields=["OBJECTID"],
                ).to_dict()
                self.assertEqual(
                    2,
                    len(retired_line_features["features"]),
                    "Did not find large remainder parcel.",
                )
            except Exception as ex:
                print(ex)
                self.fail(f"Divide failed: {ex}")

    def test_equal_width_merge_remainder_junk_values(self):
        fq_version_name = pfutils.create_version(self.vms)
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = 15
        existing_record_guid = "{18F944EA-50E9-4792-9814-FD419644934E}"
        divide_option = "EqualWidth"
        number_of_parts = 100
        divide_part_area_or_width = 100
        divide_line_bearing = 359.9
        divide_left_side = True
        divide_distribute_remainder = True
        default_area_unit = 109405
        divide_cogo_line_bearing = None

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels

            with self.assertRaises(Exception) as ex:
                parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=divide_cogo_line_bearing,
                    default_area_unit=default_area_unit,
                )
            self.assertTrue(
                str(ex.exception).startswith("Invalid function arguments"),
                f"Unexpected error message: {ex.exception}",
            )

    def test_divide_missing_parameter_correct_error(self):
        fq_version_name = pfutils.create_version(self.vms)
        divide_parcel_guid = "{3293FC07-1127-4FF6-92F1-8FF7DF663ADD}"
        divide_parcel_type = None
        existing_record_guid = "{AF818140-99D3-4DBB-B65F-98CB2C9259A8}"
        divide_option = "ProportionalArea"
        number_of_parts = None
        divide_part_area_or_width = 2010.6227237065036
        divide_line_bearing = 179.882
        divide_left_side = False
        divide_distribute_remainder = False
        default_area_unit = 109405

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            # Divide the parcels
            with self.assertRaises(Exception) as ex:
                parcel_fabric.divide(
                    divide_parcel_guid=divide_parcel_guid,
                    divide_parcel_type=divide_parcel_type,
                    divide_record=existing_record_guid,
                    divide_option=divide_option,
                    divide_number_of_parts=number_of_parts,
                    divide_part_area=divide_part_area_or_width,
                    divide_line_bearing=divide_line_bearing,
                    divide_left_side=divide_left_side,
                    divide_distribute_remainder=divide_distribute_remainder,
                    divide_cogo_line_bearing=None,
                    default_area_unit=default_area_unit,
                )
            self.assertTrue(
                "A required parameter is missing from the JSON." in str(ex.exception),
                f"Wrong error: {ex.exception}",
            )

    @classmethod
    def tearDownClass(cls):
        pfutils.clean_up_versions(cls.vms)


if __name__ == "__main__":
    unittest.main()
