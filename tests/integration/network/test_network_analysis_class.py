import unittest
import datetime
import arcgis.network as network
import arcgis.features as features
import arcgis.features.use_proximity as use_proximity
from utils.decorators import integration_test, profiles


@profiles.enterprise_and_agol
@integration_test
class TestNetworkAnalysisClass(unittest.TestCase):

    def test_solve_location_allocation_method(self):
        """Test solve_location_allocation method"""
        facil = {
            "features": [
                {
                    "attributes": {
                        "OBJECTID": 1,
                        "Name": "Facility A",
                        "FacilityType": 0,
                        "CurbApproach": 0,
                    },
                    "geometry": {
                        "x": -58.557329417999938,
                        "y": -34.587693706999971,
                    },
                },
                {
                    "attributes": {
                        "OBJECTID": 2,
                        "Name": "Facility B",
                        "FacilityType": 0,
                        "CurbApproach": 0,
                    },
                    "geometry": {
                        "x": -58.460247408999976,
                        "y": -34.683348039999942,
                    },
                },
            ]
        }
        demand_points = {
            "features": [
                {
                    "attributes": {
                        "OBJECTID": 1,
                        "Name": "Household 4",
                        "GroupName": "A",
                        "Weight": 2,
                        "CurbApproach": 0,
                    },
                    "geometry": {
                        "x": -58.664405163999959,
                        "y": -34.614819562999969,
                    },
                },
                {
                    "attributes": {
                        "OBJECTID": 2,
                        "Name": "Household 3",
                        "GroupName": "A",
                        "Weight": 2,
                        "CurbApproach": 0,
                    },
                    "geometry": {
                        "x": -58.514499119999982,
                        "y": -34.496322404999944,
                    },
                },
                {
                    "attributes": {
                        "OBJECTID": 3,
                        "Name": "Household 2",
                        "GroupName": None,
                        "Weight": 3,
                        "CurbApproach": 0,
                    },
                    "geometry": {"x": -58.54162497599998, "y": -34.788996107999935},
                },
                {
                    "attributes": {
                        "OBJECTID": 4,
                        "Name": "Household 1",
                        "GroupName": None,
                        "Weight": 5,
                        "CurbApproach": 1,
                    },
                    "geometry": {"x": -58.40599569799997, "y": -34.637662387999967},
                },
            ]
        }

        result = network.analysis.solve_location_allocation(facilities=facil, demand_points=demand_points)
        self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Routes could not be found.")

    def test_findRoutes_method(self):
        """Test find_routes method"""
        stops = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {
                            "Name": "Start point",
                            "RouteName": "Route A",
                        },
                        "geometry": {"x": -122.4079, "y": 37.78356},
                    },
                    {
                        "attributes": {"Name": "End point", "RouteName": "Route A"},
                        "geometry": {"x": -122.404, "y": 37.782},
                    },
                    {
                        "attributes": {
                            "Name": "Start point",
                            "RouteName": "Route B",
                        },
                        "geometry": {"x": -122.4095, "y": 37.78379},
                    },
                    {
                        "attributes": {"Name": "End point", "RouteName": "Route B"},
                        "geometry": {"x": -122.48, "y": 37.734},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    },
                    {
                        "name": "RouteName",
                        "type": "esriFieldTypeString",
                        "alias": "RouteName",
                        "length": "50",
                    },
                ],
            }
        )
        result = network.analysis.find_routes(stops, time_of_day=1496970000533)
        self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Routes could not be found.")

    def test_generateServiceAreas_method(self):
        """Test generate_service_areas method"""
        input_coords = {
            "x": -13045715.158400763,
            "y": 4034297.869515602,
            "spatialReference": 3857,
        }

        facility = features.FeatureSet.from_dict(
            {
                "geometryType": "esriGeometryPoint",
                "features": [{"geometry": input_coords}],
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            }
        )

        time_now = datetime.datetime.now()
        result = network.analysis.generate_service_areas(
            facilities=facility,
            break_values=30,
            break_units="Minutes",
            time_of_day=time_now,
        )
        self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Unable to generate service areas")

    def test_ClosestFacilityService_method(self):
        """Test closest_facility_service method"""
        incidents = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {
                            "CurbApproach": 0,
                            "ID": "C100045",
                            "Name": "Incident 1",
                        },
                        "geometry": {"x": -0.1891, "y": 51.5251},
                    },
                    {
                        "attributes": {
                            "CurbApproach": 0,
                            "ID": "F100086",
                            "Name": "Incident 2",
                        },
                        "geometry": {"x": -0.1884, "y": 51.5353},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "ID",
                        "type": "esriFieldTypeString",
                        "alias": "ID",
                        "length": "50",
                    },
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    },
                    {
                        "name": "CurbApproach",
                        "type": "esriFieldTypeInteger",
                        "alias": "CurbApproach",
                    },
                ],
            }
        )

        facilities = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {
                            "CurbApproach": 0,
                            "ID": "F100045",
                            "Name": "Facility 1",
                        },
                        "geometry": {"x": -0.1892, "y": 51.5252},
                    },
                    {
                        "attributes": {
                            "CurbApproach": 0,
                            "ID": "F100086",
                            "Name": "Facility 2",
                        },
                        "geometry": {"x": -0.1879, "y": 51.5256},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "ID",
                        "type": "esriFieldTypeString",
                        "alias": "ID",
                        "length": "50",
                    },
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    },
                    {
                        "name": "CurbApproach",
                        "type": "esriFieldTypeInteger",
                        "alias": "CurbApproach",
                    },
                ],
            }
        )

        time_now = datetime.datetime.now()
        result = network.analysis.find_closest_facilities(
            incidents=incidents,
            facilities=facilities,
            cutoff=30,
            time_of_day=time_now,
            number_of_facilities_to_find=2,
            distance_impedance="Miles",
        )
        self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Closest facilities could not be generated")

    def test_find_nearest_method(self):
        """Test closest_facility_service method"""
        incidents = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {
                            "CurbApproach": 0,
                            "ID": "C100045",
                            "Name": "Incident 1",
                        },
                        "geometry": {"x": -0.1891, "y": 51.5251},
                    },
                    {
                        "attributes": {
                            "CurbApproach": 0,
                            "ID": "F100086",
                            "Name": "Incident 2",
                        },
                        "geometry": {"x": -0.1884, "y": 51.5353},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "ID",
                        "type": "esriFieldTypeString",
                        "alias": "ID",
                        "length": "50",
                    },
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    },
                    {
                        "name": "CurbApproach",
                        "type": "esriFieldTypeInteger",
                        "alias": "CurbApproach",
                    },
                ],
            }
        )

        facilities = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {
                            "CurbApproach": 0,
                            "ID": "F100045",
                            "Name": "Facility 1",
                        },
                        "geometry": {"x": -0.1892, "y": 51.5252},
                    },
                    {
                        "attributes": {
                            "CurbApproach": 0,
                            "ID": "F100086",
                            "Name": "Facility 2",
                        },
                        "geometry": {"x": -0.1879, "y": 51.5256},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "ID",
                        "type": "esriFieldTypeString",
                        "alias": "ID",
                        "length": "50",
                    },
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    },
                    {
                        "name": "CurbApproach",
                        "type": "esriFieldTypeInteger",
                        "alias": "CurbApproach",
                    },
                ],
            }
        )
        incidents_fc = features.FeatureCollection.from_featureset(incidents)
        facilities_fc = features.FeatureCollection.from_featureset(facilities)
        route_service_url = self.gis.properties.helperServices.route.url
        route_service = network.RouteLayer(route_service_url, gis=self.gis)
        car_mode = [
            i
            for i in route_service.retrieve_travel_modes()["supportedTravelModes"]
            if i["name"] == "Driving Time"
        ][0]
        result = use_proximity.find_nearest(
            incidents_fc,
            facilities.to_dict(),
            measurement_type=car_mode,
            context={"outSR": {"wkid": 4326}, "inSR": {"wkid": 4326}},
            future=False,
        )
        self.assertTrue(result, "Task Unsuccessful: Closest facilities could not be generated")

    def test_OriginDestinationCostMatrix_method(self):
        """Test to check if the origin_destination_cost_matrix method"""
        origins = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {"Name": "Origin 1"},
                        "geometry": {"x": -0.1891, "y": 51.5254},
                    },
                    {
                        "attributes": {"Name": "Origin 2"},
                        "geometry": {"x": -0.1744, "y": 51.5353},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    }
                ],
            }
        )

        destinations = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {"CurbApproach": 0, "Name": "Destination 1"},
                        "geometry": {"x": -0.1991, "y": 51.5354},
                    },
                    {
                        "attributes": {"CurbApproach": 0, "Name": "Destination 2"},
                        "geometry": {"x": -0.1844, "y": 51.5458},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    },
                    {
                        "name": "CurbApproach",
                        "type": "esriFieldTypeInteger",
                        "alias": "CurbApproach",
                    },
                ],
            }
        )

        time_now = datetime.datetime.now()
        result = network.analysis.generate_origin_destination_cost_matrix(
            origins=origins,
            destinations=destinations,
            time_of_day=time_now,
            cutoff=200,
            number_of_destinations_to_find=10,
        )
        self.assertTrue(result.solve_succeeded, "Task Unsucessful: Origin-Destination cost matrix could not be generated")

    def test_LocationAllocation_service(self):
        """Test to check if the location alllocation method"""
        facilities = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {
                            "Capacity": 100,
                            "CurbApproach": 0,
                            "ID": "F100045",
                            "Name": "Facility 1",
                        },
                        "geometry": {"x": -0.1891, "y": 51.5254},
                    },
                    {
                        "attributes": {
                            "Capacity": 150,
                            "CurbApproach": 0,
                            "ID": "F100086",
                            "Name": "Facility 2",
                        },
                        "geometry": {"x": -0.1744, "y": 51.5353},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "ID",
                        "type": "esriFieldTypeString",
                        "alias": "ID",
                        "length": "50",
                    },
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    },
                    {
                        "name": "CurbApproach",
                        "type": "esriFieldTypeInteger",
                        "alias": "CurbApproach",
                    },
                    {
                        "name": "Capacity",
                        "type": "esriFieldTypeInteger",
                        "alias": "Capacity",
                    },
                ],
            }
        )

        demand_points = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {
                            "CurbApproach": 0,
                            "ID": "C00001",
                            "Name": "Customer 1",
                            "Weight": 10,
                        },
                        "geometry": {"x": -0.1891, "y": 51.5354},
                    },
                    {
                        "attributes": {
                            "CurbApproach": 1,
                            "ID": "C00002",
                            "Name": "Customer 2",
                            "Weight": 7,
                        },
                        "geometry": {"x": -0.1744, "y": 51.5453},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "ID",
                        "type": "esriFieldTypeString",
                        "alias": "ID",
                        "length": "50",
                    },
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    },
                    {
                        "name": "CurbApproach",
                        "type": "esriFieldTypeInteger",
                        "alias": "CurbApproach",
                    },
                    {
                        "name": "Weight",
                        "type": "esriFieldTypeInteger",
                        "alias": "Weight",
                    },
                ],
            }
        )

        time_now = datetime.datetime.now()
        result = network.analysis.solve_location_allocation(
            facilities=facilities,
            demand_points=demand_points,
            number_of_facilities_to_find=1,
            default_measurement_cutoff=200,
            time_of_day=time_now,
        )
        self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Location Allocation output couldnt be generated.")

    def test_edit_vehicle_routing_problem_service(self):
        """Test edit vehicle routing problem method"""
        orders = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {
                            "DeliveryQuantities": "2000 100",
                            "Name": "Order 1",
                        },
                        "geometry": {"x": -117.5254, "y": 34.111},
                    },
                    {
                        "attributes": {
                            "DeliveryQuantities": "1500 75",
                            "Name": "Order 2",
                        },
                        "geometry": {"x": -117.51, "y": 34.111},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "DeliveryQuantities",
                        "type": "esriFieldTypeString",
                        "alias": "DeliveryQuantities",
                        "length": "50",
                    },
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    },
                ],
            }
        )

        depots = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {"Name": "Depot1"},
                        "geometry": {"x": -117.52, "y": 34.117},
                    },
                    {
                        "attributes": {"Name": "Depot2"},
                        "geometry": {"x": -117.53, "y": 34.131},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    }
                ],
            }
        )

        routes = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {
                            "Capacities": "40000 2000",
                            "EndDepotName": "Depot1",
                            "Name": "Truck1",
                            "SpecialtyNames": "BucketTruck",
                            "StartDepotName": "Depot1",
                        }
                    },
                    {
                        "attributes": {
                            "Capacities": "30000 2500",
                            "EndDepotName": "Depot2",
                            "Name": "Truck2",
                            "SpecialtyNames": None,
                            "StartDepotName": "Depot2",
                        }
                    },
                ],
                "fields": [
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    },
                    {
                        "name": "Capacities",
                        "type": "esriFieldTypeString",
                        "alias": "Capacities",
                        "length": "50",
                    },
                    {
                        "name": "EndDepotName",
                        "type": "esriFieldTypeString",
                        "alias": "EndDepotName",
                        "length": "50",
                    },
                    {
                        "name": "StartDepotName",
                        "type": "esriFieldTypeString",
                        "alias": "StartDepotName",
                        "length": "50",
                    },
                    {
                        "name": "SpecialtyNames",
                        "type": "esriFieldTypeString",
                        "alias": "SpecialtyNames",
                        "length": "50",
                    },
                ],
            }
        )

        result = network.analysis.edit_vehicle_routing_problem(
            orders=orders,
            depots=depots,
            default_date=datetime.datetime.now().date(),
            routes=routes,
            populate_route_lines=True,
            populate_directions=True,
            directions_language="es",
        )
        self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Vehicle Routing Problem could not be solved.")

    def test_VehicleRoutingProblem_service(self):
        """Test vehicle routing problem method"""
        orders = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {
                            "DeliveryQuantities": "2000 100",
                            "Name": "Order 1",
                        },
                        "geometry": {"x": -117.5254, "y": 34.111},
                    },
                    {
                        "attributes": {
                            "DeliveryQuantities": "1500 75",
                            "Name": "Order 2",
                        },
                        "geometry": {"x": -117.51, "y": 34.111},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "DeliveryQuantities",
                        "type": "esriFieldTypeString",
                        "alias": "DeliveryQuantities",
                        "length": "50",
                    },
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    },
                ],
            }
        )

        depots = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {"Name": "Depot1"},
                        "geometry": {"x": -117.52, "y": 34.117},
                    },
                    {
                        "attributes": {"Name": "Depot2"},
                        "geometry": {"x": -117.53, "y": 34.131},
                    },
                ],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    }
                ],
            }
        )

        routes = features.FeatureSet.from_dict(
            {
                "features": [
                    {
                        "attributes": {
                            "Capacities": "40000 2000",
                            "EndDepotName": "Depot1",
                            "Name": "Truck1",
                            "SpecialtyNames": "BucketTruck",
                            "StartDepotName": "Depot1",
                        }
                    },
                    {
                        "attributes": {
                            "Capacities": "30000 2500",
                            "EndDepotName": "Depot2",
                            "Name": "Truck2",
                            "SpecialtyNames": None,
                            "StartDepotName": "Depot2",
                        }
                    },
                ],
                "fields": [
                    {
                        "name": "Name",
                        "type": "esriFieldTypeString",
                        "alias": "Name",
                        "length": "50",
                    },
                    {
                        "name": "Capacities",
                        "type": "esriFieldTypeString",
                        "alias": "Capacities",
                        "length": "50",
                    },
                    {
                        "name": "EndDepotName",
                        "type": "esriFieldTypeString",
                        "alias": "EndDepotName",
                        "length": "50",
                    },
                    {
                        "name": "StartDepotName",
                        "type": "esriFieldTypeString",
                        "alias": "StartDepotName",
                        "length": "50",
                    },
                    {
                        "name": "SpecialtyNames",
                        "type": "esriFieldTypeString",
                        "alias": "SpecialtyNames",
                        "length": "50",
                    },
                ],
            }
        )

        result = network.analysis.solve_vehicle_routing_problem(
            orders=orders,
            depots=depots,
            default_date=datetime.datetime.now().date(),
            routes=routes,
            populate_route_lines=True,
            populate_directions=True,
            directions_language="es",
        )
        self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Vehicle Routing Problem could not be solved.")


if __name__ == "__main__":
    unittest.main()
