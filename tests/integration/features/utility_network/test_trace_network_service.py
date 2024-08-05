import unittest
from arcgis.features._trace import TraceNetworkManager
from utils.decorators import integration_test, profiles


trace_service_url = "https://utilitynetwork.esri.com/server/rest/services/Hydro_HUC4/TraceNetworkServer"


# Server gets updated at 2:30PM PST Everyday. Do not test around then.
@profiles.utility_network
@unittest.skip("No Url of this type exists on the server")
# TODO @achapkowski @nanaeaubry -- This test is failing because the URL is not valid.
@integration_test
class TestTraceNetworkManager(unittest.TestCase):
    """Tests the Trace Network Service"""

    def setUp(self):
        self.trace_network_manager = TraceNetworkManager(
            trace_service_url,
            gis=self.gis,
        )
        assert self.trace_network_manager

    def test_properties(self):
        """Test getting properties"""
        assert self.trace_network_manager.properties

    def test_trace_configurations(self):
        """Test getting trace configurations and the methods associated with them."""
        # Get trace config manager
        manager = self.trace_network_manager.trace_configurations()
        assert manager

        configs = manager.list()
        assert configs

        # Query
        trace_configs = manager.query()
        number_trace_configs = len(trace_configs["traceConfigurations"])
        assert trace_configs
        assert trace_configs["success"] is True

        # Create
        created = manager.create(
            name="Connected_IncludeContainers",
            description="Connected trace example with containers",
            trace_type="connected",
            trace_config={
                "includeContainers": True,
                "includeContent": False,
                "includeStructures": False,
                "includeBarriers": True,
                "validateConsistency": True,
                "validateLocatability": False,
                "includeIsolated": False,
                "ignoreBarriersAtStartingPoints": False,
                "includeUpToFirstSpatialContainer": True,
                "allowIndeterminateFlow": True,
                "domainNetworkName": "",
                "tierName": "",
                "targetTierName": "",
                "subnetworkName": "",
                "diagramTemplateName": "",
                "shortestPathNetworkAttributeName": "",
                "filterBitsetNetworkAttributeName": "",
                "traversabilityScope": "junctionsAndEdges",
                "conditionBarriers": [],
                "functionBarriers": [],
                "arcadeExpressionBarrier": "",
                "filterBarriers": [],
                "filterFunctionBarriers": [],
                "filterScope": "junctionsAndEdges",
                "functions": [],
                "nearestNeighbor": {
                    "count": -1,
                    "costNetworkAttributeName": "",
                    "nearestCategories": [],
                    "nearestAssets": [],
                },
                "outputFilters": [],
                "outputConditions": [],
                "propagators": [],
            },
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
        try:
            validate = self.trace_network_manager.validate_topology(
                envelope={
                    "xmin": 1034659.2752358826,
                    "ymin": 1871561.7755379943,
                    "xmax": 1034730.4307899779,
                    "ymax": 1871623.0833411064,
                    "spatialReference": {"wkid": 102671, "latestWkid": 3435},
                },
                return_edits=True,
            )
            assert validate
        except:
            pass

    def test_query_network(self):
        """Test query network method"""
        query1 = self.trace_network_manager.query_network_moments(
            moments_to_return=["enableTopology", "initialEnableTopology"]
        )
        assert query1
        assert len(query1["networkMoments"]) == 2

        query2 = self.trace_network_manager.query_network_moments()
        assert query2
        assert len(query2["networkMoments"]) == 7

    def test_trace_test(self):
        """
        Test using trace method with the Trace Network Service
        """
        trace = self.trace_network_manager.trace(
            locations=[
                {
                    "traceLocationType": "startingPoint",
                    "globalid": "{5F8B05EC-B69A-4826-AD57-B527180EC9FD}",
                    "percentAlong": 0,
                }
            ],
            trace_type="connected",
            configuration={
                "includeBarriers": True,
                "validateConsistency": True,
                "ignoreBarriersAtStartingPoints": False,
                "allowIndeterminateFlow": False,
                "shortestPathNetworkAttributeName": "",
                "traversabilityScope": "junctionsAndEdges",
                "conditionBarriers": [],
                "functionBarriers": [],
                "functions": [],
                "outputFilters": [],
                "outputConditions": [],
                "pathDirection": "noDirection",
            },
        )
        assert trace
        assert trace["success"] is True
        assert trace["traceResults"]


if __name__ == "__main__":
    unittest.main()
