from unittest.mock import MagicMock

from utils.mocks.mock_arcgisconnection import MockArcGISConnection

class MockFeatureLayer(MagicMock):
    _dynamic_layer = None
    _token = "da78c9fb55bb5e44e44c6f88ee7d4ee4"
    url = "https://example.com/server/rest/services/Hosted/CamerTraps/FeatureServer"
    _url = url
    _con = MockArcGISConnection()
