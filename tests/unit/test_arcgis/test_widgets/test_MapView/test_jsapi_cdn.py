from unittest.mock import patch, MagicMock
import os

import pytest

from utils.mocks import MockMapView
from arcgis.widgets import MapView

arbitrary_js_cdn_str = "https://some-dns.ext/jsapi"

def _clear_jsapi_cdn_env_var():
    if "JSAPI_CDN" in os.environ:
        del os.environ["JSAPI_CDN"]

def test_jsapi_cdn_env_var_set():
    MapView.set_js_cdn("")
    mock_mapview = MockMapView()

    os.environ["JSAPI_CDN"] = arbitrary_js_cdn_str
    MapView._setup_js_cdn(mock_mapview)

    assert mock_mapview._js_cdn_override == arbitrary_js_cdn_str
    _clear_jsapi_cdn_env_var()

def test_MapView_set_js_cdn():
    _clear_jsapi_cdn_env_var()
    mock_mapview = MockMapView()

    MapView.set_js_cdn(arbitrary_js_cdn_str)
    MapView._setup_js_cdn(mock_mapview)

    assert mock_mapview._js_cdn_override == arbitrary_js_cdn_str

def test_disconn_env_jscdn_path_assembly():
    _clear_jsapi_cdn_env_var()
    MapView.set_js_cdn("")

    mock_mapview = MockMapView()
    mock_mapview._is_reachable.return_value = False
    mock_mapview.gis._url = "https://some-portal.ext/portal"

    MapView._setup_js_cdn(mock_mapview)

    assert mock_mapview._js_cdn_override == \
        "https://some-portal.ext/portal/jsapi/jsapi4/"
