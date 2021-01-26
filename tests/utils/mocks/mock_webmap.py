from unittest.mock import MagicMock

from utils.mocks.mock_gis import MockGIS

class MockWebMap(MagicMock):
    _gis = MockGIS()
    save = MagicMock()
    _webmapdict = {}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._webmapdict = {}
