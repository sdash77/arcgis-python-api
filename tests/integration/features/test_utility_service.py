import sys

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.gis import GIS
from arcgis.features._utility import UtilityNetworkManager

gis = GIS("https://utilitynetwork.esri.com/portal", "AChapkowski", "AChapkowski1")
# Create Topographic Service
try:
    utility_nm = UtilityNetworkManager(
        "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Postgres_1/UtilityNetworkServer",
        gis=gis,
    )
    assert utility_nm
    module_skip = False
except:
    print("No valid service found. Please try another service.")
    module_skip = True


@unittest.skipIf(
    module_skip, "No Utility Network Service Found. Skipping Test."
)

class TestUtilityNetworkManager(unittest.TestCase):
    """Tests the Utility Network Service"""

    def associations(self):
        """Test getting associations, querying, and traversing them"""
        assert utility_nm.associations()

        association = utility_nm.query_associations(
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

        traverse = utility_nm.traverse_associations(
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

    def locations(self):
        """Test getting locations, and querying them."""
        assert utility_nm.locations()

        locations = utility_nm.query_locations(
            max_geom_count=100,
            elements=[
                {
                    "sourceId": 16,
                    "globalIds": ["{A1094F84-42E3-4179-9236-51E1351054F8}"],
                }
            ],
            locations=True,
        )
        assert locations
        assert locations["success"] is True

    def trace_configurations(self):
        """Test getting trace configurations and the methods associated with them."""
        # Get
        assert utility_nm.trace_configurations()

        # Query
        trace_configs = utility_nm.query_trace_configurations()
        number_trace_configs = len(trace_configs["traceConfigurations"])
        assert trace_configs
        assert trace_configs["success"] is True

        # Create
        created = utility_nm.create_trace_configurations(
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
        updated_query = utility_nm.query_trace_configurations()
        assert len(updated_query["traceConfigurations"]) == number_trace_configs + 1

        # Alter
        alteration = utility_nm.alter_trace_configurations(
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
        updated_query = utility_nm.query_trace_configurations()
        assert (
            updated_query["traceConfigurations"][0]["name"]
            == "Connected_IncludeContainers_update"
        )

        # Delete
        assert utility_nm.delete_trace_configurations(
            [updated_query["traceConfigurations"][0]["globalId"]]
        )
        updated_query = utility_nm.query_trace_configurations()
        assert len(updated_query["traceConfigurations"]) == number_trace_configs

    def validate_topology(self):
        """Test validate topology method"""
        validate = utility_nm.validate_topology(
            envelope={
                "xmin": 1034659.2752358826,
                "ymin": 1871561.7755379943,
                "xmax": 1034730.4307899779,
                "ymax": 1871623.0833411064,
                "spatialReference": {"wkid": 102671, "latestWkid": 3435},
            },
            return_edits=True,
        )
    
    def query_network(self):
        """Test query network method"""
        query1 = utility_nm.query_network_moments(moments_to_return=["enableTopology","initialEnableTopology"])
        assert query1
        assert len(query1["networkMoments"]) == 2

        query2 = utility_nm.query_network_moments()
        assert query2
        assert len(query2["networkMoments"]) == 8

    def synthesize_association_geometries(self):
        """Test the method"""
        sag = utility_nm.synthesize_association_geometries(connectivity_associations=True,
                count=25,
                extent=
                {	
                "xmin": 6814287.099790375,
                    "ymin": 1847003.4894856418,
                    "xmax": 6814425.830360317,
                    "ymax": 1847091.4713699604,
                    "spatialReference": {
                        "wkid": 3498,
                        "latestWkid": 3498	
                }
                })
        assert sag
        assert sag["success"] is True
    
    def trace_test(self):
        """
        Test using trace method with the Utility Network Service
        """
        trace = utility_nm.trace(locations=[
                {
                "traceLocationType": "startingPoint",
                "globalId": "{BBF88249-6BAD-438F-9DBB-0E48DD89EECA}",
                }
                ], trace_type="subnetwork")
    
    def export_subnetwork(self):
        """Test export of subnetwork"""
        export = utility_nm.export_subnetwork(domain_name="Electric", tier_name="Electric Distribution", subnetwork_name="RMT001")

if __name__ == "__main__":
    unittest.main()
