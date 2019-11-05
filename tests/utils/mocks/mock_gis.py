from unittest.mock import MagicMock

from utils.mocks.mock_portalpy import MockPortalPy

class MockGIS(MagicMock):
    _portal = MockPortalPy()
    pass
