"""
Basic performance benchmarking.

"""

import unittest
import uuid
from datetime import datetime
import os

import perftester as pt
import pandas as pd

from integration.config import get_resource_path
from arcgis.features import FeatureLayer
from arcgis.gis import GIS, ItemProperties, ItemTypeEnum

from integration.config import _TESTS_ROOT_PATH


def get_config():
    return {
        "portal_url": os.getenv(
            "ARCGIS_TEST_PORTAL_URL", "https://geosaurus.maps.arcgis.com/"
        ),
        "username": os.getenv("ARCGIS_TEST_PORTAL_USERNAME", "arcgis_python"),
        "password": os.getenv("ARCGIS_TEST_PORTAL_PASSWORD", "amazing_arcgis_123"),
        "feature_layer_url": os.getenv(
            "ARCGIS_TEST_PORTAL_FEATURE_LAYER_URL",
            "https://services7.arcgis.com/JEwYeAy2cc8qOe3o/ArcGIS/rest/services/QueryPerformancePolygons/FeatureServer/0",
        ),
        "repetitions": int(os.getenv("ARCGIS_TEST_REPETITIONS", "10")),
    }


class TestSimplePerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = get_config()
        cls.gis = GIS(
            cls.config["portal_url"],
            cls.config["username"],
            cls.config["password"],
            verify_cert=False,
        )
        cls.layer_url = cls.config["feature_layer_url"]
        cls.results = []

    def test_construct_gis(self):
        target_benchmark_time = 1.5

        def construct_gis():
            return GIS(
                self.config["portal_url"],
                self.config["username"],
                self.config["password"],
                verify_cert=False,
            )

        val = pt.time_benchmark(
            construct_gis, Number=1, Repeat=self.config["repetitions"]
        )
        self.configure_test_result(self._testMethodName, target_benchmark_time, val)

    def test_query_feature_layer_100_features(self):
        target_benchmark_time = 1.6
        fl = FeatureLayer(self.layer_url)

        def query_feature_layer_100_features(where="objectid < 100"):
            return fl.query(where="objectid < 100")

        val = pt.time_benchmark(
            query_feature_layer_100_features,
            Number=1,
            Repeat=self.config["repetitions"],
        )
        self.configure_test_result(self._testMethodName, target_benchmark_time, val)

    def test_query_feature_layer_1000_features(self):
        target_benchmark_time = 1.2
        fl = FeatureLayer(self.layer_url)

        def query_feature_layer_1000_features():
            return fl.query(where="objectid < 1000")

        val = pt.time_benchmark(
            query_feature_layer_1000_features,
            Number=1,
            Repeat=self.config["repetitions"],
        )
        self.configure_test_result(self._testMethodName, target_benchmark_time, val)

    def test_query_feature_layer_10000_features(self):
        target_benchmark_time = 5.0
        fl = FeatureLayer(self.layer_url)

        def query_feature_layer_10000_features():
            return fl.query(where="objectid < 10000")

        val = pt.time_benchmark(
            query_feature_layer_10000_features,
            Number=1,
            Repeat=self.config["repetitions"],
        )
        self.configure_test_result(self._testMethodName, target_benchmark_time, val)

    def test_create_single_folder(self):
        target_benchmark_time = 1.1
        folders = []

        def create_single_folder():
            uid = uuid.uuid4().hex[:6]
            folder_name = f"performance_test_{uid}"
            folders.append(folder_name)
            try:
                _folder = self.gis.content.folders.create(folder_name)
                created_folder = self.gis.content.folders.get(folder_name)
                if created_folder:
                    return True
                raise Exception("The folder was not created")
            except Exception as ex:
                print(ex)

        try:
            val = pt.time_benchmark(
                create_single_folder, Number=1, Repeat=self.config["repetitions"]
            )
            self.configure_test_result(self._testMethodName, target_benchmark_time, val)
        finally:
            for folder in folders:
                existing_folder = self.gis.content.folders.get(folder)
                if existing_folder:
                    existing_folder.delete(folder)

    def test_create_folder_add_item(self):
        target_benchmark_time = 1.0
        folders = []
        item_to_add = get_resource_path("staging_data/parkinglots.zip")
        ip = ItemProperties(
            title="perf_test_item",
            item_type=ItemTypeEnum.SHAPEFILE.value,
            tags=["ntgrtn-tst"],
        )

        def create_folder_add_item():
            uid = uuid.uuid4().hex[:6]
            folder_name = f"performance_test_{uid}"
            folders.append(folder_name)
            try:
                _folder = self.gis.content.folders.create(folder_name)
                created_folder = self.gis.content.folders.get(folder_name)

                created_folder.add(item_properties=ip, file=item_to_add)
            except Exception as ex:
                print(ex)

        try:
            val = pt.time_benchmark(
                create_folder_add_item, Number=1, Repeat=self.config["repetitions"]
            )
            self.configure_test_result(self._testMethodName, target_benchmark_time, val)
        finally:
            for folder in folders:
                existing_folder = self.gis.content.folders.get(folder)
                if existing_folder:
                    existing_folder.delete(folder)

    @classmethod
    def configure_test_result(cls, test_name, benchmark, test_results):
        result_max = test_results.get("max")
        difference = (result_max / benchmark) - 1

        # Provide a 10% buffer and warn
        if difference < 0:
            passed_benchmark = "passed"
        elif 0 < difference <= 0.1:
            passed_benchmark = "warning"
        else:
            passed_benchmark = "failed"

        test_results["test_name"] = test_name
        test_results["target"] = benchmark
        test_results["difference"] = difference
        test_results["met_benchmark"] = passed_benchmark
        cls.results.append(test_results)

    @classmethod
    def tearDownClass(cls):
        tests_path = _TESTS_ROOT_PATH
        df = pd.DataFrame(
            cls.results,
            columns=[
                "test_name",
                "min",
                "mean",
                "max",
                "target",
                "difference",
                "met_benchmark",
            ],
        )
        t = datetime.now()
        file_name = str.format(
            "performance_test_results_{0}_{1}_{2}",
            str(t.year),
            str(t.month),
            str(t.day),
        )
        output_filename = os.path.join(
            tests_path, "performance", "results", f"{file_name}.csv"
        )
        df.to_csv(output_filename)
        print(f"{'='*20}\nPerformance test results saved to {output_filename}:")
        print(df[["test_name", "met_benchmark", "mean", "max", "target", "difference"]])


if __name__ == "__main__":
    unittest.main()
