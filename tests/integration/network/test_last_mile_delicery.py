#######################################################################
import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging

enable_verbose_logging()

from arcgis.features import FeatureSet
from arcgis.network._utils import find_travel_mode
from arcgis.network.analysis import solve_last_mile_delivery


@profiles.agol
# ^^^ runs tests for each profile
# sets `self.profile` to the profile name
# sets `self.gis` to the GIS for the profile, if connection is successful
# sets `self.proxies` to the detected proxies, if any
#
# see tests/utils/decorators.py for available credential and profile decorators
@integration_test
# ^^^ marks the test as an integration test
# sets the default timeout for the test
# may be enhanced with additional functionality in the future
class TestLastMileDelivery(unittest.TestCase):
    def test_last_mile_delivery(self):
        from arcgis.gis import GIS

        gis = GIS(
            profile='your_dev_online_profile',  #  need to use devext until on production
            trust_env=True,
            verify_cert=False,
        )
        travel_modes = find_travel_mode(gis=gis)
        orders: dict = {
            "features": [
                {
                    "geometry": {"x": -117, "y": 34},
                    "attributes": {
                        "Name": "Order 1",
                        "ServiceTime": 5,
                        "TimeWindowStart": None,
                        "TimeWindowEnd": 1706868000000,
                        "MaxViolationTime": 0,
                        "DeliveryQuantity_1": 2000,
                        "DeliveryQuantity_2": 100,
                    },
                },
                {
                    "geometry": {"x": -117.5, "y": 34.5},
                    "attributes": {
                        "Name": "Order 2",
                        "ServiceTime": 5,
                        "TimeWindowStart": 1706860800000,
                        "TimeWindowEnd": 1706868000000,
                        "MaxViolationTime": 30,
                        "DeliveryQuantity_1": 1500,
                        "DeliveryQuantity_2": 75,
                    },
                },
            ]
        }

        depots: dict = {
            "features": [
                {
                    "geometry": {"x": -117.2, "y": 34.2},
                    "attributes": {"Name": "Depot 1"},
                }
            ]
        }

        routes: dict = {
            "features": [
                {
                    "attributes": {
                        "Name": "Truck 1",
                        "StartDepotName": "Depot 1",
                        "EndDepotName": "Depot 1",
                        "EarliestStartTime": "6:00:00",
                        "Capacity_1": 40000,
                        "Capacity_2": 2000,
                        "CostPerUnitTime": 0.5,
                        "CostPerUnitDistance": 1.5,
                    }
                },
                {
                    "attributes": {
                        "Name": "Truck 2",
                        "StartDepotName": "Depot 1",
                        "EndDepotName": "Depot 1",
                        "EarliestStartTime": "6:00:00",
                        "Capacity_1": 30000,
                        "Capacity_2": 2500,
                        "CostPerUnitTime": 0.5,
                        "CostPerUnitDistance": 1.5,
                    }
                },
            ]
        }
        zones = {
            "features": [
                {
                    "geometry": {
                        "rings": [
                            [
                                [-97.0634, 32.8442],
                                [-97.0554, 32.84],
                                [-97.0558, 32.8327],
                                [-97.0638, 32.83],
                                [-97.0634, 32.8442],
                            ]
                        ]
                    },
                    "attributes": {"Name": "Zone 1"},
                },
                {
                    "geometry": {
                        "rings": [
                            [
                                [-97.0803, 32.8235],
                                [-97.0776, 32.8277],
                                [-97.074, 32.8254],
                                [-97.0767, 32.8227],
                                [-97.0803, 32.8235],
                            ],
                            [
                                [-97.0871, 32.8311],
                                [-97.0831, 32.8292],
                                [-97.0853, 32.8259],
                                [-97.0892, 32.8279],
                                [-97.0871, 32.8311],
                            ],
                        ]
                    },
                    "attributes": {"Name": "Zone 2"},
                },
            ]
        }
        job = solve_last_mile_delivery(
            orders=orders,
            depots=depots,
            routes=routes,
            sequence_gap=3,
            populate_directions=True,
            earliest_route_start_date="2024-02-02",
            zones=zones,
            route_specialties={
                "features": [
                    {
                        "attributes": {
                            "RouteName": "Truck 1",
                            "SpecialtyName": "Refrigerated",
                        }
                    },
                    {
                        "attributes": {
                            "RouteName": "Truck 2",
                            "SpecialtyName": "Hazmat",
                        }
                    },
                ]
            },
            locate_settings={
                "default": {
                    "allowAutoRelocate": True,
                    "tolerance": 1000,
                    "toleranceUnits": "esriMeters",
                    "sources": [{"name": "Routing_Streets"}],
                }
            },
            time_units="Minutes",
            max_route_total_time=480,
            route_shape="True Shape with Measures",
        )
        job.result()
        print('here')


if __name__ == "__main__":
    unittest.main()
