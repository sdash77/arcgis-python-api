from unittest.mock import MagicMock

class MockArcGISConnection(MagicMock):
    post = MagicMock()
    get = MagicMock()
    token = MagicMock()
    pass
