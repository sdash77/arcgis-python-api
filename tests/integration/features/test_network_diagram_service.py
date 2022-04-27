import sys

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.gis import GIS
from arcgis.features._network_diagram import NetworkDiagramManager, Diagram

gis = GIS("https://utilitynetwork.esri.com/portal", "AChapkowski", "AChapkowski1")
# Create Topographic Service
net_diag_ser = NetworkDiagramManager(
    "https://utilitynetwork.esri.com/server/rest/services/GettingToKnow_Hana/NetworkDiagramServer/diagrams",
    gis=gis,
)


class TestUtilityNetworkManager(unittest.TestCase):
    """Tests the Utility Network Service"""

    def diagrams(self):
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
    

if __name__ == "__main__":
    unittest.main()
