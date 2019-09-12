from unittest.mock import MagicMock

from utils.mocks.mock_arcgisconnection import MockArcGISConnection

class MockPortalPy(MagicMock):
    con = MockArcGISConnection()
    pass
