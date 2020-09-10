import unittest
import time
import concurrent.futures
from arcgis.gis import GIS
from arcgis.features.layer import FeatureLayerCollection
import arcgis.features


class TestAnalyzeLSA(unittest.TestCase):
    """ Apply LSA on a small fabric.  Test sync and async"""
    gis = None
    vms = None
    parcel_fabric_flc = None
    service_urls = None

    @classmethod
    def setUpClass(cls):
        # Create Python API GIS object and prepare REST service URL strings
        cls.base_server_url = "https://krennic.esri.com/server/rest/services/ApplyLSAFeet/"
        cls.gis = GIS("https://krennic.esri.com/portal",
                      "admin",
                      "esri.agp",
                      verify_cert=False)
        cls.services = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url + url for url in cls.services}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis)
        cls.vms = cls.parcel_fabric_flc.versions

    def test_apply_lsa_xy_uncertainty_async(self):
        """ Apply LSA.  Check min and max XYUncertainty values. Runs asynchronously"""
        fq_version_name = self.create_version()
        with self.vms.get(fq_version_name, "read") as version:
            # Get the Parcel Fabric.
            self.parcelFabric = arcgis.features._parcel.ParcelFabricManager(
                self.service_urls["ParcelFabricServer"], self.gis, version, self.parcel_fabric_flc)

        with self.vms.get(fq_version_name, "read"):
            is_async = True
            result = self.parcelFabric.apply_least_squares_adjustment(movement_tolerance=0.05,
                                                                      update_attributes=True,
                                                                      future=is_async)

            assert isinstance(result, concurrent.futures.Future)
            result = result.result()
            self.assertEqual("esriJobSucceeded", result["status"], f"Async job failed:\t{result['status']}")

            if not result["success"]:
                self.fail("An error occurred in Apply LSA async")

            fl = arcgis.features.FeatureLayer(f"{self.service_urls['FeatureServer']}/6", self.gis)
            lsa_result = fl.query(where="XYUncertainty IS NOT NULL",
                                  out_fields=["ObjectID", "XYUncertainty"],
                                  return_geometry=False,
                                  gdb_version=fq_version_name).to_dict()
            xyvals = []
            res_featureset = lsa_result["features"]
            for i in range(len(res_featureset)):
                xyvals.append(res_featureset[i]["attributes"]["XYUncertainty"])

            # Test for the correct XY values after Apply LSA
            self.assertAlmostEqual(16.04196267, min(
                xyvals), 3, "XY Uncertainty min value incorrect")
            self.assertAlmostEqual(25.36248208, max(
                xyvals), 3, "XY Uncertainty max value incorrect")

    def test_apply_lsa_xy_uncertainty_sync(self):
        """ Apply LSA.  Check min and max XYUncertainty values.  Runs synchronously"""
        fq_version_name = self.create_version()

        with self.vms.get(fq_version_name, "read") as version:
            # Get the Parcel Fabric.
            self.parcelFabric = arcgis.features._parcel.ParcelFabricManager(
                self.service_urls["ParcelFabricServer"], self.gis, version, self.parcel_fabric_flc)

        with self.vms.get(fq_version_name, "read"):
            is_async = False
            result = self.parcelFabric.apply_least_squares_adjustment(movement_tolerance=0.05,
                                                                      update_attributes=True,
                                                                      future=is_async)
            if not result["success"]:
                self.fail("An error occurred running Analyze LSA")

            service_edits = result["serviceEdits"]
            for i in range(len(service_edits)):
                if service_edits[i]["id"] == 6:
                    self.assertEqual(34, len(service_edits[i]["editedFeatures"]["updates"]))

    @classmethod
    def create_version(cls):
        # VersionManagementServer - Create a new version
        _version_name_txt = "api-{}".format(int(time.time()))
        cls.vms.create(_version_name_txt)

        # get the fully qualified version name string as 'owner.versionName'
        _version = [
            x for x in cls.vms.all
            if x.properties.versionName == "admin." + _version_name_txt
        ]
        fq_version_name = _version[0].properties.versionName
        return fq_version_name

    @classmethod
    def tearDownClass(cls):
        for version in cls.vms.all:
            if version.properties.versionName.startswith("admin.api-"):
                cls.assertTrue(version.delete(), "Failed to delete branch version.")


if __name__ == '__main__':
    unittest.main(
        exit=False, failfast=True, buffer=False, catchbreak=False, verbosity=1)
