import sys
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test


@integration_test
class TestCostEstimation(unittest.TestCase):
    def test_cost_estimation_all_nones(self):
        gis = GIS(
            profile="your_online_profile", verify_cert=False, proxy=detect_proxy(True)
        )
        cost = gis.content.cost()
        assert cost["transactionCreditCost"] == 0.0

    def test_cost_estimation_enterprise(self):
        gis = GIS(
            profile="your_enterprise_profile",
            verify_cert=False,
            proxy=detect_proxy(True),
        )
        assert gis.content.cost() == {}

    def test_cost_estimation(self):
        gis = GIS(
            profile="your_online_profile", verify_cert=False, proxy=detect_proxy(True)
        )
        assert gis.content.cost(
            tile_storage=None,
            file_storage=None,
            feature_storage=None,
            generate_tile_count=None,
            loaded_tile_count=None,
            enrich_variable_count=None,
            enrich_report_count=None,
            service_area_count=None,
            geocode_count=100000,
        )
        assert gis.content.cost(
            tile_storage=None,
            file_storage=None,
            feature_storage=None,
            generate_tile_count=None,
            loaded_tile_count=None,
            enrich_variable_count=None,
            enrich_report_count=None,
            service_area_count=10,
            geocode_count=None,
        )
        assert gis.content.cost(
            tile_storage=None,
            file_storage=None,
            feature_storage=None,
            generate_tile_count=None,
            loaded_tile_count=None,
            enrich_variable_count=None,
            enrich_report_count=10,
            service_area_count=None,
            geocode_count=None,
        )
        assert gis.content.cost(
            tile_storage=None,
            file_storage=None,
            feature_storage=None,
            generate_tile_count=None,
            loaded_tile_count=None,
            enrich_variable_count=10,
            enrich_report_count=None,
            service_area_count=None,
            geocode_count=None,
        )
        assert gis.content.cost(
            tile_storage=None,
            file_storage=None,
            feature_storage=None,
            generate_tile_count=None,
            loaded_tile_count=10,
            enrich_variable_count=None,
            enrich_report_count=None,
            service_area_count=None,
            geocode_count=None,
        )
        assert gis.content.cost(
            tile_storage=None,
            file_storage=None,
            feature_storage=None,
            generate_tile_count=1000,
            loaded_tile_count=None,
            enrich_variable_count=None,
            enrich_report_count=None,
            service_area_count=None,
            geocode_count=None,
        )
        assert gis.content.cost(
            tile_storage=None,
            file_storage=None,
            feature_storage=10,
            generate_tile_count=None,
            loaded_tile_count=None,
            enrich_variable_count=None,
            enrich_report_count=None,
            service_area_count=None,
            geocode_count=None,
        )
        assert gis.content.cost(
            tile_storage=None,
            file_storage=10,
            feature_storage=None,
            generate_tile_count=None,
            loaded_tile_count=None,
            enrich_variable_count=None,
            enrich_report_count=None,
            service_area_count=None,
            geocode_count=None,
        )
        assert gis.content.cost(
            tile_storage=10,
            file_storage=None,
            feature_storage=None,
            generate_tile_count=None,
            loaded_tile_count=None,
            enrich_variable_count=None,
            enrich_report_count=None,
            service_area_count=None,
            geocode_count=None,
        )


if __name__ == "__main__":
    unittest.main()
