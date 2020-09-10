import unittest
import time
import concurrent.futures
from arcgis.gis import GIS
from arcgis.features.layer import FeatureLayerCollection
import arcgis.features


class TestAnalyzeLSA(unittest.TestCase):
    """ Analyze LSA with and without parcelFeatures param on a small fabric.  Test sync and async"""
    gis = None
    vms = None
    parcel_fabric_flc = None
    service_urls = None

    @classmethod
    def setUpClass(cls):
        # Create Python API GIS object and prepare REST service URL strings
        cls.base_server_url = "https://krennic.esri.com/server/rest/services/ApplyLSA/"
        cls.gis = GIS("https://krennic.esri.com/portal",
                      "admin",
                      "esri.agp",
                      verify_cert=False)
        cls.services = ["FeatureServer",
                        "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url +
                                 url for url in cls.services}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis)
        cls.vms = cls.parcel_fabric_flc.versions

    def test_analyze_consistency_check_with_parcel_features_async(self):
        """ Analyze LSA with parcelFeatures param (simulates a selection) on small fabric.  Runs asynchronously"""
        fq_version_name = self.create_version()
        parcel_features = self.generate_parcel_features()
        with self.vms.get(fq_version_name, "read") as version:
            # Get the Parcel Fabric.
            self.parcelFabric = arcgis.features._parcel.ParcelFabricManager(
                self.service_urls["ParcelFabricServer"], self.gis, version, self.parcel_fabric_flc)

        with self.vms.get(fq_version_name, "read"):
            is_async = True
            result = self.parcelFabric.analyze_least_squares_adjustment(analysis_type="CONSISTENCY_CHECK",
                                                                        convergence_tolerance=0.05,
                                                                        parcel_features=parcel_features,
                                                                        future=is_async)
            assert isinstance(result, concurrent.futures.Future)
            result = result.result()
            self.assertEqual("esriJobSucceeded", result["status"], f"Async job failed:\t{result['status']}")

            if not result["success"]:
                self.fail("An error occurred in Apply LSA async")

            if result["success"]:
                messages = result.get("messages")
                for message in messages:
                    if message["description"] == "Chi squared:":
                        self.assertTrue("0.20" in message["description"])
                    if message["description"] == "Global (Pelzer) Reliability":
                        self.assertTrue("2.271" in message["description"])
                    if message["description"].startswith("Chi-Square test (95.0%):"):
                        self.assertTrue(
                            "FAILED" in message["description"])
            else:
                self.fail("An error occurred running Analyze LSA")

    def test_analyze_consistency_check_with_parcel_features_sync(self):
        """ Analyze LSA with parcelFeatures param (simulates a selection) on small fabric.  Runs synchronously"""
        fq_version_name = self.create_version()
        parcel_features = self.generate_parcel_features()
        with self.vms.get(fq_version_name, "read") as version:
            # Get the Parcel Fabric.
            self.parcelFabric = arcgis.features._parcel.ParcelFabricManager(
                self.service_urls["ParcelFabricServer"], self.gis, version, self.parcel_fabric_flc)

        with self.vms.get(fq_version_name, "read"):
            is_async = False
            result = self.parcelFabric.analyze_least_squares_adjustment(analysis_type="CONSISTENCY_CHECK",
                                                                        convergence_tolerance="0.05",
                                                                        parcel_features=parcel_features,
                                                                        future=is_async)
            if result["success"]:
                edits = result["serviceEdits"]
                "Find the line features"
                for i in range(len(edits)):
                    if edits[i]["id"] == 10:
                        adds = result["serviceEdits"][i]["editedFeatures"]["adds"]
                if not adds:
                    self.fail("No Line features found.")
                for i in range(len(adds)):
                    for k, v in adds[i]["attributes"].items():
                        if k == "AdjustedStdDev":
                            if v is None:
                                continue
                            self.assertTrue((6.460 < float(v) <= 6.636, 6.46094508),
                                            msg=f"Adjusted StdDev is not between 4.460 and 4.636")
            else:
                self.fail("An error occurred running Analyze LSA")

    def test_analyze_consistency_check_no_parcel_features_async(self):
        """ Analyze LSA with no parcelFeatures param (no selection) on small fabric.  Runs asynchronously"""
        fq_version_name = self.create_version()

        with self.vms.get(fq_version_name, "read") as version:
            # Get the Parcel Fabric.
            self.parcelFabric = arcgis.features._parcel.ParcelFabricManager(
                self.service_urls["ParcelFabricServer"], self.gis, version, self.parcel_fabric_flc)
        with self.vms.get(fq_version_name, "read"):
            is_async = True
            result = self.parcelFabric.analyze_least_squares_adjustment(analysis_type="CONSISTENCY_CHECK",
                                                                        convergence_tolerance="0.05",
                                                                        future=is_async)
            assert isinstance(result, concurrent.futures.Future)
            result = result.result()
            self.assertEqual("esriJobSucceeded", result["status"], f"Async job failed:\t{result['status']}")
            if result["success"]:
                messages = result.get("messages")
                for message in messages:
                    if message["description"].startswith("Chi squared:"):
                        actual = message["description"][message["description"].index(": ") + 1:].strip()
                        self.assertAlmostEqual(
                            59.85, float(actual), delta=0.05)
                    if message["description"].startswith("Global (Pelzer) Reliability:"):
                        start_idx = message["description"].index(": ") + 1
                        end_idx = message["description"].index(" (ex")
                        actual = message["description"][start_idx: end_idx].strip()
                        self.assertAlmostEqual(
                            15.667, float(actual), delta=0.5)
                    if message["description"].startswith("Chi-Square test (95.0%):"):
                        # description has format "x < y < z".  Split between < into a dict.  Compare key to value
                        actual = message["description"][len("Chi-Square test (95.0%): "): -7].split("<")
                        comparator_dict = dict(zip([0.65, 1.5, 1.5], actual))
                        for k, v in comparator_dict.items():
                            self.assertAlmostEqual(float(k), float(v), delta=0.05,
                                                   msg="Chi Square range values incorrect.")
            else:
                self.fail("An error occurred running Analyze LSA")

    def test_analyze_consistency_check_no_parcel_features_sync(self):
        """ Analyze LSA with no parcelFeatures param (no selection) on small fabric.  Runs synchronously"""
        fq_version_name = self.create_version()

        with self.vms.get(fq_version_name, "read") as version:
            # Get the Parcel Fabric.
            self.parcelFabric = arcgis.features._parcel.ParcelFabricManager(
                self.service_urls["ParcelFabricServer"], self.gis, version, self.parcel_fabric_flc)

        with self.vms.get(fq_version_name, "read"):
            is_async = False
            result = self.parcelFabric.analyze_least_squares_adjustment(analysis_type="CONSISTENCY_CHECK",
                                                                        convergence_tolerance="0.05",
                                                                        future=is_async)
            if result["success"]:
                adds = result["serviceEdits"][0]["editedFeatures"]["adds"]
                for i in range(len(adds)):
                    for k, v in adds[i]["attributes"].items():
                        if k == "ZUncertainty":
                            self.assertEqual(
                                v, 0.03215217, "ZUncertainty is incorrect")
            else:
                self.fail("An error occurred running Analyze LSA")

    def test_analyze_weighted_LSA_with_parcel_features_async(self):
        """ Analyze LSA with parcelFeatures param (simulates a selection) on small fabric.  Runs a synchronously"""
        fq_version_name = self.create_version()
        parcel_features = self.generate_parcel_features()

        with self.vms.get(fq_version_name, "read") as version:
            # Get the Parcel Fabric.
            self.parcelFabric = arcgis.features._parcel.ParcelFabricManager(
                self.service_urls["ParcelFabricServer"], self.gis, version, self.parcel_fabric_flc)

        with self.vms.get(fq_version_name, "read"):
            is_async = True
            result = self.parcelFabric.analyze_least_squares_adjustment(analysis_type="WEIGHTED_LEAST_SQUARES",
                                                                        convergence_tolerance="0.05",
                                                                        parcel_features=parcel_features,
                                                                        future=is_async)
            assert isinstance(result, concurrent.futures.Future)
            result = result.result()
            self.assertEqual("esriJobSucceeded", result["status"], f"Async job failed:\t{result['status']}")
            if result["success"]:
                for message in result.get("messages"):
                    if message["description"] == "Chi squared:":
                        self.assertTrue("0.13" in message["description"])
                    if message["description"] == "Global (Pelzer) Reliability":
                        self.assertTrue("2.583" in message["description"])
                    if message["description"].startswith("Chi-Square test (95.0%):"):
                        self.assertTrue(
                            "0.000 < 0.000 < 0.000 FAILED" in message["description"])
            else:
                self.fail("An error occurred running Analyze LSA")

    def test_analyze_weighted_LSA_with_parcel_features_sync(self):
        """ Analyze LSA with parcelFeatures param (simulates a selection) on small fabric.  Runs synchronously"""
        fq_version_name = self.create_version()
        parcel_features = self.generate_parcel_features()

        with self.vms.get(fq_version_name, "read") as version:
            # Get the Parcel Fabric.
            self.parcelFabric = arcgis.features._parcel.ParcelFabricManager(
                self.service_urls["ParcelFabricServer"], self.gis, version, self.parcel_fabric_flc)

        with self.vms.get(fq_version_name, "read"):
            is_async = False
            result = self.parcelFabric.analyze_least_squares_adjustment(analysis_type="WEIGHTED_LEAST_SQUARES",
                                                                        convergence_tolerance="0.05",
                                                                        parcel_features=parcel_features,
                                                                        future=is_async)
            # wait a couple seconds to let
            time.sleep(2)
            if result["success"]:
                edits = result["serviceEdits"]
                "Find the line features"
                for i in range(len(edits)):
                    if edits[i]["id"] == 9:
                        adds = result["serviceEdits"][i]["editedFeatures"]["adds"]
                self.assertTrue(adds, "No service edits for lines FC")
                adj_x_vals = []
                adj_y_vals = []
                for i in range(len(adds)):
                    for k, v in adds[i]["attributes"].items():
                        if k == "AdjustedX":
                            adj_x_vals.append(v)
                        if k == "AdjustedY":
                            adj_y_vals.append(v)
            else:
                self.fail("The Analyze function failed")

            self.assertTrue(len(adj_x_vals) == 12, "Adjust X not found in results")
            self.assertTrue(len(adj_y_vals) == 12, "Adjust Y not found in results")

            self.assertAlmostEqual(7717973.09142832, min(
                adj_x_vals), delta=0.005, msg="Adjusted X minimum value is incorrect")
            self.assertAlmostEqual(7720644.48520308, max(
                adj_x_vals), delta=0.0005, msg="Adjusted X maximum value is incorrect")
            self.assertAlmostEqual(629647.44794996, min(
                adj_y_vals), delta=0.0005, msg="Adjusted Y minimum value is incorrect")
            self.assertAlmostEqual(631577.57524533, max(
                adj_y_vals), delta=0.0005, msg="Adjusted Y maximum value is incorrect")

    def test_analyze_weighted_LSA_no_parcel_features_async(self):
        """ Analyze LSA with no parcelFeatures param (no selection) on small fabric.  Runs asynchronously"""
        fq_version_name = self.create_version()

        with self.vms.get(fq_version_name, "read") as version:
            # Get the Parcel Fabric.
            self.parcelFabric = arcgis.features._parcel.ParcelFabricManager(
                self.service_urls["ParcelFabricServer"], self.gis, version, self.parcel_fabric_flc)

        with self.vms.get(fq_version_name, "read"):
            is_async = True
            result = self.parcelFabric.analyze_least_squares_adjustment(analysis_type="WEIGHTED_LEAST_SQUARES",
                                                                        convergence_tolerance="0.05",
                                                                        future=is_async)
            assert isinstance(result, concurrent.futures.Future)
            result = result.result()
            self.assertEqual("esriJobSucceeded", result["status"], f"Async job failed:\t{result['status']}")
            if result["success"]:
                messages = result.get("messages")
                for message in messages:
                    if message["description"] == "Chi squared:":
                        self.assertTrue("59.72" in message["description"])
                    if message["description"] == "Global (Pelzer) Reliability":
                        self.assertTrue("17.668" in message["description"])
                    if message["description"].startswith("Chi-Square test (95.0%):"):
                        self.assertTrue(
                            "0.615 < 1.456 < 1.477 PASSED" in message["description"])
            else:
                self.fail("An error occurred running Analyze LSA")

    def test_analyze_weighted_LSA_no_parcel_features_sync(self):
        """ Analyze LSA with no parcelFeatures param (no selection) on small fabric.  Runs synchronously"""
        fq_version_name = self.create_version()

        with self.vms.get(fq_version_name, "read") as version:
            # Get the Parcel Fabric.
            self.parcelFabric = arcgis.features._parcel.ParcelFabricManager(
                self.service_urls["ParcelFabricServer"], self.gis, version, self.parcel_fabric_flc)

        with self.vms.get(fq_version_name, "read"):
            is_async = False
            result = self.parcelFabric.analyze_least_squares_adjustment(analysis_type="WEIGHTED_LEAST_SQUARES",
                                                                        convergence_tolerance="0.05",
                                                                        future=is_async)
            if result["success"]:
                adds = result["serviceEdits"][0]["editedFeatures"]["adds"]
                for i in range(len(adds)):
                    for k, v in adds[i]["attributes"].items():
                        if k == "ZUncertainty":
                            self.assertEqual(
                                v, 0.03215217, "ZUncertainty is incorrect")
            else:
                self.fail("An error occurred running Analyze LSA")

    @classmethod
    def generate_parcel_features(cls):
        return [{'id': '{0CAA7157-2BD3-43E7-AC5B-4ADA176F504F}', 'layerId': 13},
                {'id': '{D469B37D-BC4F-4479-8249-EEC4B61CE257}', 'layerId': 13},
                {'id': '{18C76BC1-290B-4B95-B3C7-2ACF7AAF3F4D}', 'layerId': 13},
                {'id': '{D8F48375-72E5-4E6C-9424-B61E13C6F421}', 'layerId': 13},
                {'id': '{31C49C49-9AAD-45BE-BFEF-A1DB9E6283BD}', 'layerId': 13},
                {'id': '{DD488A83-CF66-4403-83F3-BA4D5D1633B0}', 'layerId': 13},
                {'id': '{BE87EBF0-05CB-48EA-A65F-00B9DD302CCA}', 'layerId': 13},
                {'id': '{0DF60010-0A72-4BEB-82A4-F4F20A3566F1}', 'layerId': 13},
                {'id': '{73D07072-EBFE-4CD3-A01F-E0BBFA2B1A1F}', 'layerId': 13},
                {'id': '{4F3EA6CE-68D0-428B-A88F-2378E840D132}', 'layerId': 13},
                {'id': '{3E28D656-07EF-4A94-BDE7-B834A2CB6E0D}', 'layerId': 13},
                {'id': '{91185D29-A94A-42B9-AB8C-61225E87005A}', 'layerId': 13}]

    @classmethod
    def create_version(cls):
        try:
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
        except Exception as ex:
            print(ex)
            return None

    @classmethod
    def tearDownClass(cls):
        for version in cls.vms.all:
            if version.properties.versionName.startswith("admin.api-"):
                cls.assertTrue(version.delete(), "Failed to delete branch version.")


if __name__ == '__main__':
    unittest.main(failfast=True, buffer=False, catchbreak=False, verbosity=1)
