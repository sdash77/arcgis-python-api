import unittest
from unittest.mock import patch, MagicMock
import os

from utils.mocks import MockMapView
from arcgis.widgets import MapView

arbitrary_js_cdn_str = "https://some-dns.ext/jsapi"


class TestJsapiCdn(unittest.TestCase):

    def _clear_jsapi_cdn_env_var(self):
        if "JSAPI_CDN" in os.environ:
            del os.environ["JSAPI_CDN"]

    def test_jsapi_cdn_env_var_set(self):
        MapView.set_js_cdn("")
        mock_mapview = MockMapView()

        os.environ["JSAPI_CDN"] = arbitrary_js_cdn_str
        MapView._setup_js_cdn(mock_mapview)

        assert mock_mapview._js_cdn_override == arbitrary_js_cdn_str
        self._clear_jsapi_cdn_env_var()

    def test_MapView_set_js_cdn(self):
        self._clear_jsapi_cdn_env_var()
        mock_mapview = MockMapView()

        MapView.set_js_cdn(arbitrary_js_cdn_str)
        MapView._setup_js_cdn(mock_mapview)

        assert mock_mapview._js_cdn_override == arbitrary_js_cdn_str

    def test_disconn_env_jscdn_path_assembly(self):
        self._clear_jsapi_cdn_env_var()
        MapView.set_js_cdn("")

        mock_mapview = MockMapView()
        mock_mapview._is_reachable.return_value = False
        mock_mapview.gis._url = "https://some-portal.ext/portal"

        MapView._setup_js_cdn(mock_mapview)

        assert (
            mock_mapview._js_cdn_override == "https://some-portal.ext/portal/jsapi/jsapi4/"
        )


if __name__ == "__main__":

    unittest.main()
