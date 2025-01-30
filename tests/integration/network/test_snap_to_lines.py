import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging
from arcgis.gis import GIS
from arcgis.network.analysis import snap_to_roads
from arcgis.features import FeatureSet

enable_verbose_logging()


@profiles.devext
@integration_test
class TestSnapToRoads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        cls.points = points = {
            "features": [
                {
                    "attributes": {
                        "OBJECTID": 1,
                        "location_timestamp": 1704522159000,
                    },
                    "geometry": {
                        "x": -122.43410099956145,
                        "y": 37.800155000053394,
                    },
                },
                {
                    "attributes": {
                        "OBJECTID": 2,
                        "location_timestamp": 1704522171000,
                    },
                    "geometry": {
                        "x": -122.43459799999755,
                        "y": 37.800737999958812,
                    },
                },
                {
                    "attributes": {
                        "OBJECTID": 3,
                        "location_timestamp": 1704522183000,
                    },
                    "geometry": {
                        "x": -122.43539199974094,
                        "y": 37.800955000073259,
                    },
                },
                {
                    "attributes": {
                        "OBJECTID": 4,
                        "location_timestamp": 1704522195000,
                    },
                    "geometry": {
                        "x": -122.43629900019869,
                        "y": 37.800787999566637,
                    },
                },
                {
                    "attributes": {
                        "OBJECTID": 5,
                        "location_timestamp": 1704522231000,
                    },
                    "geometry": {
                        "x": -122.43627299989902,
                        "y": 37.800661000005221,
                    },
                },
                {
                    "attributes": {
                        "OBJECTID": 6,
                        "location_timestamp": 1704522247000,
                    },
                    "geometry": {
                        "x": -122.43612999959976,
                        "y": 37.800168999799666,
                    },
                },
            ]
        }
        cls.travel_mode = {
            "attributeParameterValues": [
                {
                    "attributeName": "TravelTime",
                    "parameterName": "Vehicle Maximum Speed (km/h)",
                    "value": 0,
                },
                {
                    "attributeName": "Avoid Carpool Roads",
                    "parameterName": "Restriction Usage",
                    "value": "PROHIBITED",
                },
                {
                    "attributeName": "Avoid Express Lanes",
                    "parameterName": "Restriction Usage",
                    "value": "PROHIBITED",
                },
                {
                    "attributeName": "Avoid Gates",
                    "parameterName": "Restriction Usage",
                    "value": "AVOID_MEDIUM",
                },
                {
                    "attributeName": "Avoid Private Roads",
                    "parameterName": "Restriction Usage",
                    "value": "AVOID_MEDIUM",
                },
                {
                    "attributeName": "Avoid Unpaved Roads",
                    "parameterName": "Restriction Usage",
                    "value": "AVOID_HIGH",
                },
                {
                    "attributeName": "Driving an Automobile",
                    "parameterName": "Restriction Usage",
                    "value": "PROHIBITED",
                },
                {
                    "attributeName": "Roads Under Construction Prohibited",
                    "parameterName": "Restriction Usage",
                    "value": "PROHIBITED",
                },
                {
                    "attributeName": "Through Traffic Prohibited",
                    "parameterName": "Restriction Usage",
                    "value": "AVOID_HIGH",
                },
            ],
            "description": "Models the movement of cars and other similar small automobiles, such as pickup trucks, and finds solutions that optimize travel time. Travel obeys one-way roads, avoids illegal turns, and follows other rules that are specific to cars. When you specify a start time, dynamic travel speeds based on traffic are used where it is available.",
            "distanceAttributeName": "Kilometers",
            "id": "FEgifRtFndKNcJMJ",
            "impedanceAttributeName": "TravelTime",
            "name": "Driving Time",
            "restrictionAttributeNames": [
                "Avoid Carpool Roads",
                "Avoid Express Lanes",
                "Avoid Gates",
                "Avoid Private Roads",
                "Avoid Unpaved Roads",
                "Driving an Automobile",
                "Roads Under Construction Prohibited",
                "Through Traffic Prohibited",
            ],
            "simplificationTolerance": 10,
            "simplificationToleranceUnits": "esriMeters",
            "timeAttributeName": "TravelTime",
            "type": "AUTOMOBILE",
            "useHierarchy": True,
            "uturnAtJunctions": "esriNFSBAtDeadEndsAndIntersections",
        }
        cls.return_lines = True
        cls.road_properties_on_snapped_points = [
            "posted_speed_limit_mph",
            "posted_speed_limit_mps",
        ]
        cls.road_properties_on_lines = ["length_miles"]

    def test_basic_usage(self):
        result = snap_to_roads(
            points=self.points,
            road_properties_on_snapped_points=self.road_properties_on_snapped_points,
            return_lines=self.return_lines,
            road_properties_on_lines=self.road_properties_on_lines,
        )
        assert result.output_snapped_points
        assert isinstance(result.output_snapped_points, FeatureSet)
        assert result.output_lines
        assert isinstance(result.output_lines, FeatureSet)

    def test_no_road_returns_fs_input(self):
        from arcgis.features import FeatureSet

        fs = FeatureSet.from_dict(self.points)
        result = snap_to_roads(
            points=fs,
            return_lines=False,
        )
        assert result.output_snapped_points
        assert isinstance(result.output_snapped_points, FeatureSet)
        assert result.output_lines is None

    def test_no_road_returns(self):
        result = snap_to_roads(
            points=self.points,
            return_lines=False,
        )
        assert result.output_snapped_points
        assert isinstance(result.output_snapped_points, FeatureSet)
        assert result.output_lines is None


if __name__ == "__main__":
    unittest.main()
