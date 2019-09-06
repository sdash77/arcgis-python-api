#-------------------------------------------------------------------------------
# Name:        network analysis module tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import datetime
import os

#region PreCondition check
test_skip = False
class_skip = False
module_skip = False

r1 = PreconditionChecks.check_API_import()
r2 = PreconditionChecks.check_Python_version()

if (r1 & r2):
    print("## Precondition checks passed ##")
    module_skip = False
else:
    module_skip = True
    print("Pre condition checks failed. Quitting tests")
    raise(exit())

# Import the module after Precondition checks pass
try:
    import arcgis
    from arcgis.gis import GIS
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in GIS module")
def setUpModule():
    """
    Set up code for full arcgis.gis module GIS class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_NetworkAnalysisModule(unittest.TestCase):
    """
    Test to check if a UserManager object works with builtin portal
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """

        #region Read config data
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['teamportal']['url']
        cls.portal_username = _conf_reader['teamportal']['admin_user']
        cls.portal_password = _conf_reader['teamportal']['admin_password']

        # _conf_reader2 = ConfigParser()
        # _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')
        #
        # cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        # cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_UserManager_cls']
        # #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_UserManager_portal_builtin class")
        #endregion

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_NetworkAnalysis_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def test_solve_location_allocation_method(self):
        """
        Test to check if the solve_location_allocation method of network analysis module works without throwing an error.
        :return:
        """
        try:

            import arcgis.network as network
            import arcgis.features as features
            facil = {"features":[{"attributes":{"OBJECTID":1,"Name":"Facility A","FacilityType":0,"CurbApproach":0},"geometry":{"x":-58.557329417999938,"y":-34.587693706999971}},
                                 {"attributes":{"OBJECTID":2,"Name":"Facility B","FacilityType":0,"CurbApproach":0},"geometry":{"x":-58.460247408999976,"y":-34.683348039999942}}]}
            demand_points = {"features":[{"attributes":{"OBJECTID":1,"Name":"Household 4","GroupName":"A","Weight":2,"CurbApproach":0},"geometry":{"x":-58.664405163999959,"y":-34.614819562999969}},
                                         {"attributes":{"OBJECTID":2,"Name":"Household 3","GroupName":"A","Weight":2,"CurbApproach":0},"geometry":{"x":-58.514499119999982,"y":-34.496322404999944}},
                                         {"attributes":{"OBJECTID":3,"Name":"Household 2","GroupName":None,"Weight":3,"CurbApproach":0},"geometry":{"x":-58.54162497599998,"y":-34.788996107999935}},
                                         {"attributes":{"OBJECTID":4,"Name":"Household 1","GroupName":None,"Weight":5,"CurbApproach":1},"geometry":{"x":-58.40599569799997,"y":-34.637662387999967}}]}

            result = network.analysis.solve_location_allocation(facilities=facil,
                                                             demand_points=demand_points)
            if result.solve_succeeded:
                print(result)

            self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Routes could not be found.")


        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


    def test_findRoutes_method(self):
        """
        Test to check if the find_routes method of network analysis module works without throwing an error.
        :return:
        """
        try:

            import arcgis.network as network
            import arcgis.features as features

            stops = features.FeatureSet.from_dict({
                "features": [{"attributes": {"Name": "Start point", "RouteName": "Route A"},
                              "geometry": {"x": -122.4079, "y": 37.78356}},
                             {"attributes": {"Name": "End point", "RouteName": "Route A"},
                              "geometry": {"x": -122.404, "y": 37.782}},
                             {"attributes": {"Name": "Start point", "RouteName": "Route B"},
                              "geometry": {"x": -122.4095, "y": 37.78379}},
                             {"attributes": {"Name": "End point", "RouteName": "Route B"},
                              "geometry": {"x": -122.48, "y": 37.734}}],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"},
                    {"name": "RouteName", "type": "esriFieldTypeString", "alias": "RouteName", "length": "50"}
                ]
            })


            result = network.analysis.find_routes(stops, time_of_day=1496970000533)

            if result.solve_succeeded:
                print(result)

            self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Routes could not be found.")


        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


    def test_generateServiceAreas_method(self):
        """
        Test to check if the generate_service_areas method of network analysis module works without throwing an error.
        :return:
        """
        try:


            import arcgis.network as network
            import arcgis.features as features

            input_coords = {"x": -13045715.158400763, "y": 4034297.869515602, "spatialReference": 3857}

            facility = features.FeatureSet.from_dict({"geometryType": "esriGeometryPoint",
                                                      "features": [{"geometry": input_coords}],
                                                      "spatialReference": {"wkid": 102100,
                                                                           "latestWkid": 3857}})

            time_now = datetime.datetime.now()
            result = network.analysis.generate_service_areas(facilities=facility, break_values=30,
                                                             break_units="Minutes", time_of_day=time_now)

            if result.solve_succeeded:
                print(result)

            self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Unable to generate service areas")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_ClosestFacilityService_method(self):
        """
        Test to check if the closest_facility_service method of network analysis module works without throwing an error.
        :return:
        """
        try:

            import arcgis.network as network
            import arcgis.features as features

            incidents = features.FeatureSet.from_dict({
                "features": [{"attributes": {"CurbApproach": 0,
                                             "ID": "C100045",
                                             "Name": "Incident 1"},
                              "geometry": {"x": -0.1891, "y": 51.5251}},
                             {"attributes": {"CurbApproach": 0,
                                             "ID": "F100086",
                                             "Name": "Incident 2"},
                              "geometry": {"x": -0.1884, "y": 51.5353}}],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {"name": "ID", "type": "esriFieldTypeString", "alias": "ID", "length": "50"},
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"},
                    {"name": "CurbApproach", "type": "esriFieldTypeInteger", "alias": "CurbApproach"}
                ]})

            facilities = features.FeatureSet.from_dict({
                "features": [{"attributes": {"CurbApproach": 0,
                                             "ID": "F100045",
                                             "Name": "Facility 1"},
                              "geometry": {"x": -0.1892, "y": 51.5252}},
                             {"attributes": {"CurbApproach": 0,
                                             "ID": "F100086",
                                             "Name": "Facility 2"},
                              "geometry": {"x": -0.1879, "y": 51.5256}}],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {"name": "ID", "type": "esriFieldTypeString", "alias": "ID", "length": "50"},
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"},
                    {"name": "CurbApproach", "type": "esriFieldTypeInteger", "alias": "CurbApproach"}
                ]})

            time_now = datetime.datetime.now()
            result = network.analysis.find_closest_facilities(incidents=incidents, facilities=facilities,
                                                              cutoff=30, time_of_day=time_now,
                                                              number_of_facilities_to_find=2,
                                                              distance_impedance="Miles")

            if result.solve_succeeded:
                print(result)

            self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Closest facilities could not be generated")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


    def test_OriginDestinationCostMatrix_method(self):
        """
        Test to check if the origin_destination_cost_matrix method of network analysis module works without throwing an error.
        :return:
        """
        try:

            import arcgis.network as network
            import arcgis.features as features

            origins = features.FeatureSet.from_dict({
                "features": [{"attributes": {"Name": "Origin 1"},
                              "geometry": {"x": -0.1891, "y": 51.5254}},
                             {"attributes": {"Name": "Origin 2"},
                              "geometry": {"x": -0.1744, "y": 51.5353}}],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"}
                ]})

            destinations = features.FeatureSet.from_dict({
                "features": [{"attributes": {"CurbApproach": 0,
                                             "Name": "Destination 1"},
                              "geometry": {"x": -0.1991, "y": 51.5354}},
                             {"attributes": {"CurbApproach": 0,
                                             "Name": "Destination 2"},
                              "geometry": {"x": -0.1844, "y": 51.5458}}],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"},
                    {"name": "CurbApproach", "type": "esriFieldTypeInteger", "alias": "CurbApproach"}
                ]})

            time_now = datetime.datetime.now()
            result = network.analysis.generate_origin_destination_cost_matrix(origins=origins,
                                                                              destinations=destinations,
                                                                              time_of_day=time_now, cutoff=200,
                                                                              number_of_destinations_to_find=10)

            if result.solve_succeeded:
                print(result)

            self.assertTrue(result.solve_succeeded, "Task Unsucessful : Origin-Destination cost matrix could not be generated")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


    def test_LocationAllocation_service(self):
        """
        Test to check if the location alllocation method of network analysis module works without throwing an error.
        :return:
        """
        try:

            import arcgis.network as network
            import arcgis.features as features

            facilities = features.FeatureSet.from_dict({
                "features": [{"attributes": {"Capacity": 100,
                                             "CurbApproach": 0,
                                             "ID": "F100045",
                                             "Name": "Facility 1"},
                              "geometry": {"x": -0.1891, "y": 51.5254}},
                             {"attributes": {"Capacity": 150,
                                             "CurbApproach": 0,
                                             "ID": "F100086",
                                             "Name": "Facility 2"},
                              "geometry": {"x": -0.1744, "y": 51.5353}}],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {"name": "ID", "type": "esriFieldTypeString", "alias": "ID", "length": "50"},
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"},
                    {"name": "CurbApproach", "type": "esriFieldTypeInteger", "alias": "CurbApproach"},
                    {"name": "Capacity", "type": "esriFieldTypeInteger", "alias": "Capacity"}
                ]
            })

            demand_points = features.FeatureSet.from_dict({
                "features": [{"attributes": {"CurbApproach": 0,
                                             "ID": "C00001",
                                             "Name": "Customer 1",
                                             "Weight": 10},
                              "geometry": {"x": -0.1891, "y": 51.5354}},
                             {"attributes": {"CurbApproach": 1,
                                             "ID": "C00002",
                                             "Name": "Customer 2",
                                             "Weight": 7},
                              "geometry": {"x": -0.1744, "y": 51.5453}}],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {"name": "ID", "type": "esriFieldTypeString", "alias": "ID", "length": "50"},
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"},
                    {"name": "CurbApproach", "type": "esriFieldTypeInteger", "alias": "CurbApproach"},
                    {"name": "Weight", "type": "esriFieldTypeInteger", "alias": "Weight"}
                ]
            })

            time_now = datetime.datetime.now()
            result = network.analysis.solve_location_allocation(facilities=facilities, demand_points=demand_points,
                                                                number_of_facilities_to_find=1,
                                                                default_measurement_cutoff=200,
                                                                time_of_day=time_now)
            if result.solve_succeeded:
                print(result)

            self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Location Allocation output couldnt be generated.")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_edit_vehicle_routing_problem_service(self):
        """
        Test to check if the edit vehicle routing problem of network analysis module works without throwing an error.
        :return:
        """
        try:

            import arcgis.network as network
            import arcgis.features as features

            orders = features.FeatureSet.from_dict({
                "features": [{"attributes": {"DeliveryQuantities": "2000 100",
                                             "Name": "Order 1"},
                              "geometry": {"x": -117.5254, "y": 34.111}},
                             {"attributes": {"DeliveryQuantities": "1500 75",
                                             "Name": "Order 2"},
                              "geometry": {"x": -117.51, "y": 34.111}}],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {"name": "DeliveryQuantities", "type": "esriFieldTypeString", "alias": "DeliveryQuantities",
                     "length": "50"},
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"}
                ]
            })

            depots = features.FeatureSet.from_dict({
                "features": [{"attributes": {"Name": "Depot1"},
                              "geometry": {"x": -117.52, "y": 34.117}},
                             {"attributes": {"Name": "Depot2"},
                              "geometry": {"x": -117.53, "y": 34.131}}],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"}
                ]
            })

            routes = features.FeatureSet.from_dict({
                "features": [{"attributes": {"Capacities": "40000 2000",
                                             "EndDepotName": "Depot1",
                                             "Name": "Truck1",
                                             "SpecialtyNames": "BucketTruck",
                                             "StartDepotName": "Depot1"}},
                             {"attributes": {"Capacities": "30000 2500",
                                             "EndDepotName": "Depot2",
                                             "Name": "Truck2",
                                             "SpecialtyNames": None,
                                             "StartDepotName": "Depot2"}}],
                "fields": [
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"},
                    {"name": "Capacities", "type": "esriFieldTypeString", "alias": "Capacities", "length": "50"},
                    {"name": "EndDepotName", "type": "esriFieldTypeString", "alias": "EndDepotName",
                     "length": "50"},
                    {"name": "StartDepotName", "type": "esriFieldTypeString", "alias": "StartDepotName",
                     "length": "50"},
                    {"name": "SpecialtyNames", "type": "esriFieldTypeString", "alias": "SpecialtyNames",
                     "length": "50"}
                ]
            })

            result = network.analysis.edit_vehicle_routing_problem(orders=orders, depots=depots,
                                                                    default_date=datetime.datetime.now().date(),
                                                                    routes=routes, populate_route_lines=True,
                                                                    populate_directions=True,
                                                                    directions_language="es")

            if result.solve_succeeded:
                print(result)

            self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Vehicle Routing Problem could not be solved.")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
    def test_VehicleRoutingProblem_service(self):
        """
        Test to check if the vehicle routing problem of network analysis module works without throwing an error.
        :return:
        """
        try:

            import arcgis.network as network
            import arcgis.features as features

            orders = features.FeatureSet.from_dict({
                "features": [{"attributes": {"DeliveryQuantities": "2000 100",
                                             "Name": "Order 1"},
                              "geometry": {"x": -117.5254, "y": 34.111}},
                             {"attributes": {"DeliveryQuantities": "1500 75",
                                             "Name": "Order 2"},
                              "geometry": {"x": -117.51, "y": 34.111}}],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {"name": "DeliveryQuantities", "type": "esriFieldTypeString", "alias": "DeliveryQuantities",
                     "length": "50"},
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"}
                ]
            })

            depots = features.FeatureSet.from_dict({
                "features": [{"attributes": {"Name": "Depot1"},
                              "geometry": {"x": -117.52, "y": 34.117}},
                             {"attributes": {"Name": "Depot2"},
                              "geometry": {"x": -117.53, "y": 34.131}}],
                "spatialReference": {"wkid": 4326, "latestWkid": 4326},
                "geometryType": "esriGeometryPoint",
                "fields": [
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"}
                ]
            })

            routes = features.FeatureSet.from_dict({
                "features": [{"attributes": {"Capacities": "40000 2000",
                                             "EndDepotName": "Depot1",
                                             "Name": "Truck1",
                                             "SpecialtyNames": "BucketTruck",
                                             "StartDepotName": "Depot1"}},
                             {"attributes": {"Capacities": "30000 2500",
                                             "EndDepotName": "Depot2",
                                             "Name": "Truck2",
                                             "SpecialtyNames": None,
                                             "StartDepotName": "Depot2"}}],
                "fields": [
                    {"name": "Name", "type": "esriFieldTypeString", "alias": "Name", "length": "50"},
                    {"name": "Capacities", "type": "esriFieldTypeString", "alias": "Capacities", "length": "50"},
                    {"name": "EndDepotName", "type": "esriFieldTypeString", "alias": "EndDepotName",
                     "length": "50"},
                    {"name": "StartDepotName", "type": "esriFieldTypeString", "alias": "StartDepotName",
                     "length": "50"},
                    {"name": "SpecialtyNames", "type": "esriFieldTypeString", "alias": "SpecialtyNames",
                     "length": "50"}
                ]
            })

            result = network.analysis.solve_vehicle_routing_problem(orders=orders, depots=depots,
                                                                    default_date=datetime.datetime.now().date(),
                                                                    routes=routes, populate_route_lines=True,
                                                                    populate_directions=True,
                                                                    directions_language="es")

            if result.solve_succeeded:
                print(result)

            self.assertTrue(result.solve_succeeded, "Task Unsuccessful: Vehicle Routing Problem could not be solved.")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def tearDown(self):
        print("------------------------------------------------------------------\n")

