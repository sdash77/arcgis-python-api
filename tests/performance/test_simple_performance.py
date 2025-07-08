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

def get_config():
    return {
        "portal_url": os.getenv("ARCGIS_TEST_PORTAL_URL", "https://dev0016752.esri.com/portal"),
        "username": os.getenv("ARCGIS_TEST_PORTAL_USERNAME", "admin"),
        "password": os.getenv("ARCGIS_TEST_PORTAL_PASSWORD", "esri.agp"),
        "feature_layer_url": os.getenv("ARCGIS_TEST_PORTAL_FEATURE_LAYER_URL", "https://dev0016752.esri.com/server/rest/services/HCADFull/FeatureServer/15")
    }

class TestSimplePerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = get_config()
        cls.gis = GIS(
            cls.config["portal_url"], cls.config["username"], cls.config["password"], verify_cert=False
        )
        cls.layer_url = (
            cls.config["feature_layer_url"]
        )
        cls.results = []

    def test_construct_gis(self):
        target_benchmark_time = 0.6

        def construct_gis():
            return GIS(self.config["portal_url"], self.config["username"], self.config["password"], verify_cert=False)

        val = pt.time_benchmark(construct_gis, Number=1, Repeat=10)
        self.configure_test_benchmark(self._testMethodName, target_benchmark_time, val)

    def test_query_feature_layer_100_features(self):
        target_benchmark_time = 0.7
        fl = FeatureLayer(self.layer_url)

        def query_feature_layer_100_features(where="objectid < 100"):
            return fl.query(where="objectid < 100")

        val = pt.time_benchmark(
            query_feature_layer_100_features,
            Number=1,
            Repeat=10,
        )
        self.configure_test_benchmark(self._testMethodName, target_benchmark_time, val)

    def test_query_feature_layer_1000_features(self):
        target_benchmark_time = 0.8
        fl = FeatureLayer(self.layer_url)

        def query_feature_layer_1000_features():
            return fl.query(where="objectid < 1000")

        val = pt.time_benchmark(query_feature_layer_1000_features, Number=1, Repeat=10)
        self.configure_test_benchmark(self._testMethodName, target_benchmark_time, val)

    ###
    def test_query_feature_layer_10000_features(self):
        target_benchmark_time = 9.0
        fl = FeatureLayer(self.layer_url)

        def query_feature_layer_10000_features():
            return fl.query(where="objectid < 10000")

        val = pt.time_benchmark(query_feature_layer_10000_features, Number=1, Repeat=10)
        self.configure_test_benchmark(self._testMethodName, target_benchmark_time, val)

    def test_create_single_folder(self):
        target_benchmark_time = 0.5
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
            val = pt.time_benchmark(create_single_folder, Number=1, Repeat=10)
            self.configure_test_benchmark(
                self._testMethodName, target_benchmark_time, val
            )
        finally:
            for folder in folders:
                existing_folder = self.gis.content.folders.get(folder)
                if existing_folder:
                    existing_folder.delete(folder)

    def test_create_folder_add_item(self):
        target_benchmark_time = 0.5
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
            val = pt.time_benchmark(create_folder_add_item, Number=1, Repeat=10)
            self.configure_test_benchmark(
                self._testMethodName, target_benchmark_time, val
            )
        finally:
            for folder in folders:
                existing_folder = self.gis.content.folders.get(folder)
                if existing_folder:
                    existing_folder.delete(folder)

    @classmethod
    def configure_test_benchmark(cls, test_name, benchmark, test_results):
        passed_benchmark = "failed"
        if benchmark > test_results.get("max"):
            passed_benchmark = "passed"
        test_results["test_name"] = test_name
        test_results["target"] = benchmark
        test_results["met_benchmark"] = passed_benchmark
        cls.results.append(test_results)

    @classmethod
    def tearDownClass(cls):
        df = pd.DataFrame(
            cls.results,
            columns=["test_name", "min", "mean", "max", "target", "met_benchmark"],
        )
        t = datetime.now()
        file_name = str.format(
            "performance_test_results_{0}_{1}_{2}",
            str(t.year),
            str(t.month),
            str(t.day),
        )
        df.to_csv(f"./results/{file_name}.csv")


if __name__ == "__main__":
    unittest.main()
