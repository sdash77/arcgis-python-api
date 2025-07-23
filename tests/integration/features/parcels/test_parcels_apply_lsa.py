import unittest
import time
import concurrent.futures
from arcgis.gis import GIS
from arcgis.features.layer import FeatureLayerCollection
import arcgis.features
from utils.decorators import integration_test, profiles
from . import parcel_fabric_utils as pfutils


@profiles.parcel_fabric
@integration_test
class TestApplyLSA(unittest.TestCase):
    """Apply LSA on a small fabric.  Test sync and async"""

    gis = None
    vms = None
    parcel_fabric_flc = None
    service_urls = None

    @classmethod
    def setUpClass(cls):
        # Create Python API GIS object and prepare REST service URL strings
        cls.base_server_url = (
            "https://dev0016752.esri.com/server/rest/services/ParcelFabric_LSA/"
        )

        cls.services = [
            "FeatureServer",
            "ParcelFabricServer",
            "VersionManagementServer",
        ]
        cls.service_urls = {url: cls.base_server_url + url for url in cls.services}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis
        )
        cls.vms = cls.parcel_fabric_flc.versions

    def test_apply_lsa_xy_uncertainty_async(self):
        """Apply LSA.  Check min and max XYUncertainty values. Runs asynchronously"""
        fq_version_name = pfutils.create_version(self.vms)
        with self.vms.get(fq_version_name, "read") as version:
            # Get the Parcel Fabric.
            self.parcelFabric = arcgis.features._parcel.ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )

        with self.vms.get(fq_version_name, "read"):
            is_async = True
            result = self.parcelFabric.apply_least_squares_adjustment(
                movement_tolerance=0.05, update_attributes=True, future=is_async
            )

            assert isinstance(result, concurrent.futures.Future)
            result = result.result()
            self.assertEqual(
                "esriJobSucceeded",
                result["status"],
                f"Async job failed:\t{result['status']}",
            )

            if not result["success"]:
                self.fail("An error occurred in Apply LSA async")

            fl = arcgis.features.FeatureLayer(
                f"{self.service_urls['FeatureServer']}/10", self.gis
            )
            lsa_result = fl.query(
                where="XYUncertainty IS NOT NULL",
                out_fields=["ObjectID", "XYUncertainty"],
                return_geometry=False,
                gdb_version=fq_version_name,
            ).to_dict()
            xyvals = []
            res_featureset = lsa_result["features"]
            for i in range(len(res_featureset)):
                xyvals.append(res_featureset[i]["attributes"]["XYUncertainty"])

            # Test for the correct XY values after Apply LSA
            self.assertAlmostEqual(
                16.04196267, min(xyvals), 2, "XY Uncertainty min value incorrect"
            )
            self.assertAlmostEqual(
                25.36248208, max(xyvals), 2, "XY Uncertainty max value incorrect"
            )

    def test_apply_lsa_xy_uncertainty_sync(self):
        """Apply LSA.  Check min and max XYUncertainty values.  Runs synchronously"""
        fq_version_name = pfutils.create_version(self.vms)

        with self.vms.get(fq_version_name, "read") as version:
            # Get the Parcel Fabric.
            self.parcelFabric = arcgis.features._parcel.ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )

        with self.vms.get(fq_version_name, "read"):
            is_async = False
            result = self.parcelFabric.apply_least_squares_adjustment(
                movement_tolerance=0.05, update_attributes=True, future=is_async
            )
            if not result["success"]:
                self.fail("An error occurred running Analyze LSA")

            service_edits = result["serviceEdits"]
            for i in range(len(service_edits)):
                if service_edits[i]["id"] == 6:
                    self.assertEqual(
                        34, len(service_edits[i]["editedFeatures"]["updates"])
                    )

    @classmethod
    def tearDownClass(cls):
        pfutils.clean_up_versions(cls.vms)


if __name__ == "__main__":
    unittest.main(
        exit=False, failfast=True, buffer=False, catchbreak=False, verbosity=1
    )
