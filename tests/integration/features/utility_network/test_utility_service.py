import json
import unittest
import urllib.request

import requests

from arcgis.features._utility import UtilityNetworkManager
from arcgis.features._trace_configuration import TraceConfiguration
from utils.decorators import integration_test, profiles

utility_network_url = "https://utilitynetwork.esri.com/server/rest/services/NapervilleElectric31_SQLServer/UtilityNetworkServer"


# Server gets updated at 2:30PM PST Everyday. Do not test around then.
@profiles.utility_network
@integration_test
class TestUtilityNetworkManager(unittest.TestCase):
    """Tests the Utility Network Service"""

    def setUp(self):
        self.utility_network_manager = UtilityNetworkManager(
            utility_network_url, gis=self.gis
        )
        assert self.utility_network_manager

    def test_associations(self):
        """Test getting associations, querying, and traversing them"""
        assert self.utility_network_manager.associations()

        association = self.utility_network_manager.query_associations(
            types=["containment"],
            elements=[
                {
                    "networkSourceId": 19,
                    "globalId": "{AE323515-8E6F-4CC2-B9A8-1DB963E769AB}",
                }
            ],
        )
        assert association
        assert association["success"] is True

        traverse = self.utility_network_manager.traverse_associations(
            direction="ascending",
            stop_at_first_spatial=False,
            elements=[
                {
                    "networkSourceId": 19,
                    "globalId": "{AE323515-8E6F-4CC2-B9A8-1DB963E769AB}",
                }
            ],
        )
        assert traverse
        assert traverse["success"] is True

    def test_locations(self):
        """Test getting locations, and querying them."""
        assert self.utility_network_manager.locations()

        locations = self.utility_network_manager.query_locations(
            max_geom_count=100,
            elements=[
                {
                    "sourceId": 16,
                    "globalIds": ["{A1094F84-42E3-4179-9236-51E1351054F8}"],
                }
            ],
            locations=True,
        )
        self.assertIsNotNone(locations, "Locations object is None")
        self.assertTrue(locations["success"], "Locations result not successful")
        self.assertTrue(len(locations) >= 1, "Unexpected length of Locations result")
        self.assertIsNotNone(
            locations["objects"][0]["globalId"], "Result global ID is emtpy"
        )

    def test_trace_configurations(self):
        """Test getting trace configurations and the methods associated with them."""
        # Get trace config manager
        manager = self.utility_network_manager.trace_configurations()
        assert manager

        configs = manager.list()
        assert configs

        # Query
        trace_configs = manager.query()
        number_trace_configs = len(trace_configs["traceConfigurations"])
        assert trace_configs
        assert trace_configs["success"] is True

        # Try out TraceConfiguration class
        a_trace = trace_configs["traceConfigurations"][0]
        trace_config = TraceConfiguration.from_config(a_trace["traceConfiguration"])

        assert trace_config
        assert isinstance(trace_config.to_dict(), dict)

        new_config = TraceConfiguration(
            include_containers=True,
            include_content=False,
            include_structures=False,
            include_barriers=True,
            validate_consistency=True,
            validate_locatability=False,
            include_isolated=False,
            ignore_barriers_at_starting_points=False,
            include_up_to_first_spatial_container=True,
            allow_indeterminate_flow=True,
            domain_network_name="",
            tier_name="",
            target_tier_name="",
            subnetwork_name="",
            shortest_path_network_attribute_name="",
            filter_bitset_network_attribute_name="",
            traversability_scope="junctionsAndEdges",
            condition_barriers=[],
            function_barriers=[],
            filter_barriers=[],
            filter_function_barriers=[],
            filter_scope="junctionsAndEdges",
            functions=[],
            nearest_neighbor={
                "count": -1,
                "costNetworkAttributeName": "",
                "nearestCategories": [],
                "nearestAssets": [],
            },
            output_filters=[],
            output_conditions=[],
            propagators=[],
        )
        # Create
        created = manager.create(
            name="Connected_IncludeContainers",
            description="Connected trace example with containers",
            trace_type="connected",
            trace_config=new_config,
            result_types=[
                {
                    "type": "elements",
                    "includeGeometry": False,
                    "includePropagatedValues": False,
                    "networkAttributeNames": [],
                    "diagramTemplateName": "",
                    "resultTypeFields": [],
                }
            ],
            tags=["Connected", "Include_Containers"],
        )
        assert created
        updated_query = manager.query()
        assert len(updated_query["traceConfigurations"]) == number_trace_configs + 1

        # Alter
        alteration = manager.alter(
            global_id=[
                tc["globalId"]
                for tc in updated_query["traceConfigurations"]
                if tc["name"] == "Connected_IncludeContainers"
            ][0],
            name="Connected_IncludeContainers_update",
            description="Connected trace example with containers (updated 112020)",
            result_types=[
                {
                    "type": "aggregatedGeometry",
                    "includeGeometry": False,
                    "includePropagatedValues": False,
                    "networkAttributeNames": [],
                    "diagramTemplateName": "",
                    "resultTypeFields": [],
                }
            ],
        )
        assert alteration
        updated_query = manager.query()
        assert "Connected_IncludeContainers_update" in [
            tc["name"] for tc in updated_query["traceConfigurations"]
        ]

        # Delete
        gbl_id = [
            cfg["globalId"]
            for cfg in updated_query["traceConfigurations"]
            if cfg["name"] == "Connected_IncludeContainers_update"
        ][0]

        assert manager.delete([gbl_id])
        updated_query = manager.query()
        assert len(updated_query["traceConfigurations"]) == number_trace_configs

    def test_validate_topology(self):
        """Test validate topology method. Validate edit made to network. If improper then gets marked as dirty rather than clean."""
        with self.assertRaises(Exception) as ex:
            validate = self.utility_network_manager.validate_topology(
                envelope={
                    "xmin": 1034659.2752358826,
                    "ymin": 1871561.7755379943,
                    "xmax": 1034730.4307899779,
                    "ymax": 1871623.0833411064,
                    "spatialReference": {"wkid": 102671, "latestWkid": 3435},
                },
                return_edits=True,
            )
        self.assertTrue(
            "A dirty area is not present within the validate network topology input extent."
            in str(ex.exception),
            f"Unexpected exception occurred: {str(ex.exception)}",
        )

    def test_query_network(self):
        """Test query network method"""
        query1 = self.utility_network_manager.query_network_moments(
            moments_to_return=["enableTopology", "initialEnableTopology"]
        )
        assert query1
        assert len(query1["networkMoments"]) == 2

        query2 = self.utility_network_manager.query_network_moments()
        assert query2
        assert len(query2["networkMoments"]) == 8

    def test_synthesize_association_geometries(self):
        """Test the method"""
        sag = self.utility_network_manager.synthesize_association_geometries(
            connectivity_associations=True,
            count=25,
            extent={
                "xmin": 6814287.099790375,
                "ymin": 1847003.4894856418,
                "xmax": 6814425.830360317,
                "ymax": 1847091.4713699604,
                "spatialReference": {"wkid": 3498, "latestWkid": 3498},
            },
        )
        assert sag
        assert sag["success"] is True

    def test_trace_test(self):
        """
        Test using trace method with the Utility Network Service
        """
        trace_configs = TraceConfiguration(
            domain_network_name="Electric",
            tier_name="Electric Distribution",
            condition_barriers=[
                {
                    "name": "E:Device Status",
                    "type": "networkAttribute",
                    "operator": "equal",
                    "value": 1,
                    "combineUsingOr": True,
                    "isSpecificValue": True,
                },
                {
                    "name": "Lifecycle Status",
                    "type": "networkAttribute",
                    "operator": "doesNotIncludeAny",
                    "value": 24,
                    "combineUsingOr": False,
                    "isSpecificValue": True,
                },
            ],
        )
        trace = self.utility_network_manager.trace(
            locations=[
                {
                    "traceLocationType": "startingPoint",
                    "globalId": "{2F82291C-ED2E-40F5-AB36-FEB0C50E3353}",
                    "terminalId": 16,
                }
            ],
            trace_type="subnetwork",
            configuration=trace_configs,
            result_types=[
                {
                    "type": "features",
                    "includeGeometry": False,
                    "includePropagatedValues": False,
                    "networkAttributeNames": [],
                    "diagramTemplateName": "",
                    "resultTypeFields": [],
                }
            ],
        )
        assert trace
        assert trace["success"] is True
        trace_features = trace.get("traceResults").get("featureElements")
        trace_features_count = len(trace_features)
        self.assertTrue(
            trace_features_count > 6000,
            f"Incorrect count of trace features returned: {trace_features_count}",
        )

    def test_export_subnetwork(self):
        export = self.utility_network_manager.export_subnetwork(
            domain_name="electric",
            tier_name="Electric Distribution",
            subnetwork_name="RMT001",
            result_types=[
                {
                    "type": "associations",
                    "includeGeometry": False,
                    "includePropagatedValues": False,
                    "networkAttributeNames": [],
                    "diagramTemplateName": "",
                    "resultTypeFields": [],
                }
            ],
        )
        assert export
        assert export["success"] is True
        result_type_query = urllib.request.urlopen(export.get("url"))
        result_type_result = json.loads(result_type_query.read())
        self.assertEqual(
            1708,
            len(result_type_result.get("associations")),
            "Incorrect quantity of result associations",
        )

    @unittest.skip("This test no longer throws an exception")
    def test_export_dirty_subnetwork_fails(self):
        """Test export of subnetwork"""
        with self.assertRaises(Exception) as ex:
            export = self.utility_network_manager.export_subnetwork(
                domain_name="electric",
                tier_name="Electric Distribution",
                subnetwork_name="RMT001",
            )
            assert export
            assert export["success"] is True
        self.assertTrue(
            "Dirty subnetwork" in str(ex.exception),
            f"Unexpected error message: {str(ex.exception)}",
        )
        # except Exception as e:
        #     if "Dirty subnetwork" in e.args[0]:
        #         # This is an expected error if we don't have a clean subnetwork.
        #         return True


if __name__ == "__main__":
    unittest.main()
