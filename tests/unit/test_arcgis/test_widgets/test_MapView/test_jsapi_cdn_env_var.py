from unittest.mock import patch, MagicMock
import os

import pytest

from utils.mocks import MockMapView
from arcgis.widgets import MapView

#@patch("ipywidgets.dlink")
def test_jsapi_cdn_env_var_set():
    os.environ["JSAPI_CDN"] = "https://some-dns.ext/jsapi/"
    raise Exception("Failed on purpose")

def test_jsapi_cdn_env_var_not_set():
     raise Exception("Failed on purpose")

