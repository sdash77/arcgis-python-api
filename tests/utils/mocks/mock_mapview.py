from uuid import uuid4

from unittest.mock import MagicMock
from utils.mocks.mock_gis import MockGIS

class MockMapView(MagicMock):
    _mapview_uuid_to_dlinks = {}
    _synced_mapviews = []
    gis = MockGIS()
    _uuid = ""

    def __init__(self, *args, **kwargs):
        super(MagicMock, self).__init__(*args, **kwargs)
        self._uuid = uuid4()
        self._synced_mapviews = []
        self._mapview_uuid_to_dlinks = {}

    pass
