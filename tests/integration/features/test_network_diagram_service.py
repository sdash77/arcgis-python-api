import sys
import unittest

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
from arcgis.gis import GIS
from arcgis.features._network_diagram import NetworkDiagramManager, Diagram

gis = GIS("https://utilitynetwork.esri.com/portal", "AChapkowski", "AChapkowski1")


class TestUtilityNetworkManager(unittest.TestCase):
    """Tests the Utility Network Service"""

    def diagrams(self):
        net_diag_ser = NetworkDiagramManager(
            "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Hana/NetworkDiagramServer",
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
        lyr_defs = diagram.layer_definitions(all_layers=True)
        assert lyr_defs
        assert "layerDefinitions" in lyr_defs

        # Get diagram map
        map = diagram.identify_diagram_map(
            geometry="1034510, 1871808, 1034512, 1871809",
            geometry_type="esriGeometryEnvelope",
            tolerance=2,
            image_display="496,496,96",
            map_extent={
                1034222.0452205092,
                1871589.0737789422,
                1034702.7306108437,
                1871863.8619432747,
            },
        )
        assert map

    def find_diagrams(self):
        net_diag_ser = NetworkDiagramManager(
            "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Hana/NetworkDiagramServer",
            gis=gis,
        )

        names = net_diag_ser.find_diagram_names()
        assert names
        assert "diagramNames" in names

        infos = net_diag_ser.find_diagram_infos(diagrams_names=names["diagramNames"])
        assert infos
        assert "diagramInfos" in infos

    def query_consistency_states(self):
        net_diag_ser = NetworkDiagramManager(
            "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Hana/NetworkDiagramServer",
            gis=gis,
        )

        names = net_diag_ser.find_diagram_names()
        const_states = net_diag_ser.query_consistency_state(names["diagramNames"])
        assert const_states
        assert len(const_states) == len(names["diagramNames"])

    def templates(self):
        net_diag_ser = NetworkDiagramManager(
            "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Hana/NetworkDiagramServer",
            gis=gis,
        )

        templates = net_diag_ser.templates
        assert templates

        template = net_diag_ser.template(templates["templates"][0])
        assert template
        assert "creationDate" in template

    def dataset(self):
        net_diag_ser = NetworkDiagramManager(
            "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Hana/NetworkDiagramServer",
            gis=gis,
        )

        dataset = net_diag_ser.diagram_dataset
        assert dataset
        assert "diagramTemplateInfos" in dataset


if __name__ == "__main__":
    unittest.main()
