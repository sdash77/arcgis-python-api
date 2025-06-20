import unittest
from arcgis.features._network_diagram import NetworkDiagramManager, Diagram
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

diagram_service_url = (
    "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow25_Postgres/NetworkDiagramServer"
)

enable_verbose_logging()


@profiles.utility_network
@integration_test
class TestUtilityNetworkManager(unittest.TestCase):
    """Tests the Utility Network Service"""

    def test_diagrams(self):
        net_diag_ser = NetworkDiagramManager(
            diagram_service_url,
            gis=self.gis,
        )
        """Test Diagrams and Diagram methods"""
        # Get all diagrams
        diagrams = net_diag_ser.diagrams()
        assert diagrams

        # Get one diagram
        diagram = net_diag_ser.diagram("Basic_ppp1")
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

    def test_find_diagrams(self):
        net_diag_ser = NetworkDiagramManager(
            diagram_service_url,
            gis=self.gis,
        )

        names = net_diag_ser.find_diagram_names()
        assert names
        assert "diagramNames" in names

        infos = net_diag_ser.find_diagram_infos(diagrams_names=names["diagramNames"])
        assert infos
        assert "diagramInfos" in infos

    def test_query_consistency_states(self):
        net_diag_ser = NetworkDiagramManager(
            diagram_service_url,
            gis=self.gis,
        )

        names = net_diag_ser.find_diagram_names()
        const_states = net_diag_ser.query_consistency_state(names["diagramNames"])
        assert const_states
        assert len(const_states) == len(names["diagramNames"])

    def test_templates(self):
        net_diag_ser = NetworkDiagramManager(
            diagram_service_url,
            gis=self.gis,
        )

        templates = net_diag_ser.templates
        assert templates

        template = net_diag_ser.template(templates["templates"][0])
        assert template
        assert "creationDate" in template

    def test_dataset(self):
        net_diag_ser = NetworkDiagramManager(
            diagram_service_url,
            gis=self.gis,
        )

        dataset = net_diag_ser.diagram_dataset
        assert dataset
        assert "diagramTemplateInfos" in dataset


if __name__ == "__main__":
    unittest.main()
