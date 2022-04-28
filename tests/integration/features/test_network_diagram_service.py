import sys

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.gis import GIS
from arcgis.features._network_diagram import NetworkDiagramManager, Diagram

gis = GIS("https://utilitynetwork.esri.com/portal", "AChapkowski", "AChapkowski1")


class TestUtilityNetworkManager(unittest.TestCase):
    """Tests the Utility Network Service"""

    def diagrams(self):
        net_diag_ser = NetworkDiagramManager(
            "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Hana/NetworkDiagramServer/diagrams",
            gis=gis,
        )
        """Test Diagrams and Diagram methods"""
        # Get all diagrams
        diagrams = net_diag_ser.diagrams()
        assert diagrams

        # Get one diagram
        diagram = net_diag_ser.diagram("basicex_testing")
        assert diagram
        assert isinstance(diagram, Diagram)

        # Get flags and Clear flags
        flags = diagram.get_flags("esriDiagramRootJunction")
        assert flags

        # Get Assertions
        assertions = diagram.get_aggregations()
        assert assertions

        # Get Layer Definitions
        lyr_def = diagram.layer_definitions(all_layers=True)
        assert lyr_def

        # Get diagram map
        map = diagram.identify_diagram_map(
            geometry={}, tolerance=0, image_display="", map_extent={}
        )
        assert map

    def find_diagrams(self):
        net_diag_ser = NetworkDiagramManager(
            "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Hana/NetworkDiagramServer/diagrams",
            gis=gis,
        )

        names = net_diag_ser.find_diagram_names()
        assert names

        infos = net_diag_ser.find_diagram_infos(diagrams_names=names)
        assert infos

    def query_consistency_states(self):
        net_diag_ser = NetworkDiagramManager(
            "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Hana/NetworkDiagramServer/diagrams",
            gis=gis,
        )

        names = net_diag_ser.find_diagram_names()
        const_states = net_diag_ser.query_consistency_state(names)
        assert const_states

    def templates(self):
        net_diag_ser = NetworkDiagramManager(
            "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Hana/NetworkDiagramServer/diagrams",
            gis=gis,
        )

        templates = net_diag_ser.templates
        assert templates

        template = net_diag_ser.template(templates[0])
        assert template

    def dataset(self):
        net_diag_ser = NetworkDiagramManager(
            "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Hana/NetworkDiagramServer/diagrams",
            gis=gis,
        )

        dataset = net_diag_ser.diagram_dataset
        assert dataset


if __name__ == "__main__":
    unittest.main()
