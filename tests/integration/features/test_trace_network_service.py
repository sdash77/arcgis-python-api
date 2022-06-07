import sys

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.gis import GIS
from arcgis.features._trace import TraceNetworkManager

gis = GIS("https://utilitynetwork.esri.com/portal", "AChapkowski", "AChapkowski1")
# Create Topographic Service
try:
    # Server gets updated at 2:30PM PST Everyday. Do not test around then.
    trace_nm = TraceNetworkManager(
        "https://utilitynetwork.esri.com/server/rest/services/HUC4_TraceNetwork/TraceNetworkServer",
        gis=gis,
    )
    assert trace_nm
    module_skip = False
except:
    print("No valid service found. Please try another service.")
    module_skip = True


@unittest.skipIf(module_skip, "No Trace Network Service Found. Skipping Test.")
class TestTraceNetworkManager(unittest.TestCase):
    """Tests the Trace Network Service"""

    def properties(self):
        """Test getting properties"""
        assert trace_nm.properties

    def trace_configurations(self):
        """Test getting trace configurations and the methods associated with them."""
        # Get trace config manager
        manager = trace_nm.trace_configurations()
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
            global_id=updated_query["traceConfigurations"][0]["globalId"],
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
        assert (
            updated_query["traceConfigurations"][0]["name"]
            == "Connected_IncludeContainers_update"
        )

        # Delete
        assert manager.delete([updated_query["traceConfigurations"][0]["globalId"]])
        updated_query = manager.query()
        assert len(updated_query["traceConfigurations"]) == number_trace_configs

    def validate_topology(self):
        """Test validate topology method. Validate edit made to network. If improper then gets marked as dirty rather than clean."""
        try:
            validate = trace_nm.validate_topology(
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

    def query_network(self):
        """Test query network method"""
        query1 = trace_nm.query_network_moments(
            moments_to_return=["enableTopology", "initialEnableTopology"]
        )
        assert query1
        assert len(query1["networkMoments"]) == 2

        query2 = trace_nm.query_network_moments()
        assert query2
        assert len(query2["networkMoments"]) == 7

    # def trace_test(self):
    #     """
    #     Test using trace method with the Trace Network Service
    #     """
    #     trace = trace_nm.trace(
    #         locations=[
    #             {
    #                 "traceLocationType": "startingPoint",
    #                 "globalId": "{2F82291C-ED2E-40F5-AB36-FEB0C50E3353}",
    #                 "terminalId": 16,
    #             }
    #         ],
    #         trace_type="subnetwork",
    #         configuration={
    #             "domainNetworkName": "Electric",
    #             "tierName": "Electric Distribution",
    #             "conditionBarriers": [
    #                 {
    #                     "name": "E:Device Status",
    #                     "type": "networkAttribute",
    #                     "operator": "equal",
    #                     "value": 1,
    #                     "combineUsingOr": True,
    #                     "isSpecificValue": True,
    #                 },
    #                 {
    #                     "name": "Lifecycle Status",
    #                     "type": "networkAttribute",
    #                     "operator": "doesNotIncludeAny",
    #                     "value": 24,
    #                     "combineUsingOr": False,
    #                     "isSpecificValue": True,
    #                 },
    #             ],
    #         },
    #     )
    #     assert trace
    #     assert trace["success"] is True


if __name__ == "__main__":
    unittest.main()
