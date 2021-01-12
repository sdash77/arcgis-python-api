from unittest.mock import patch, MagicMock

import pytest

from utils.mocks import MockMapView
from arcgis.widgets import MapView

def test_anon_gis():
    mock_anon_mapview = MockMapView()
    mock_anon_mapview.gis._portal.con.token = None
    MapView._setup_default_basemap(mock_anon_mapview)
    assert mock_anon_mapview.basemap
    #== "osm"

def test_credential_gis():
    mock_anon_mapview = MockMapView()
    mock_anon_mapview.gis._portal.con.token = "dfd94efdca7deba4326101d55e0d2912"
    MapView._setup_default_basemap(mock_anon_mapview)
    assert mock_anon_mapview.basemap != "osm"
