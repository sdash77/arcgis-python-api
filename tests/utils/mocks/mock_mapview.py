from unittest.mock import MagicMock

from utils.mocks.mock_gis import MockGIS

class MockMapView(MagicMock):
    gis = MockGIS()
    pass
