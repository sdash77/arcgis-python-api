from unittest.mock import MagicMock

from utils.mocks.mock_arcgisconnection import MockConnection

class MockPortalPy(MagicMock):
    con = MockConnection()
    pass
