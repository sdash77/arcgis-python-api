import unittest
from arcgis.auth.tools import parse_url
from arcgis.auth._auth._token import _parse_arcgis_url
from urllib.parse import ParseResult


class TestParseUrl(unittest.TestCase):
    """tests the parse_url"""

    def test_parse_url(self):
        """tests the parse url process"""
        parsed = parse_url(url="https://www.arcgis.com")
        assert parsed
        assert isinstance(parsed, ParseResult)
        assert parsed.scheme == "https"
        assert parsed.netloc == "www.arcgis.com"
        assert not parsed.path
        assert not parsed.params
        assert not parsed.query
        assert not parsed.fragment

class TestURLParseLogic(unittest.TestCase):
    """tests the parse logic for the token url"""

    def test_test_parse_logic(self):
        assert _parse_arcgis_url(url=None) == "https://www.arcgis.com"
        assert (
            _parse_arcgis_url(url="https://www.arcgis.com")
            == "https://www.arcgis.com"
        )
        assert (
            _parse_arcgis_url(url="https://www.arcgis.com/sharing/rest")
            == "https://www.arcgis.com"
        )
        assert (
            _parse_arcgis_url(url="https://www.arcgis.com/sharing")
            == "https://www.arcgis.com"
        )
        assert (
            _parse_arcgis_url(
                url="http://pythonapi.playground.esri.com/portal"
            )
            == "http://pythonapi.playground.esri.com/portal"
        )
        assert (
            _parse_arcgis_url(
                url="http://pythonapi.playground.esri.com/portal/home"
            )
            == "http://pythonapi.playground.esri.com/portal"
        )
        assert (
            _parse_arcgis_url(
                url="http://pythonapi.playground.esri.com/portal/sharing/rest"
            )
            == "http://pythonapi.playground.esri.com/portal"
        )
        assert (
            _parse_arcgis_url(
                url="http://pythonapi.playground.esri.com/portal/sharing/rest"
            )
            == "http://pythonapi.playground.esri.com/portal"
        )
        assert (
            _parse_arcgis_url(
                url="https://pythonapi.playground.esri.com/portal/sharing/rest"
            )
            == "https://pythonapi.playground.esri.com/portal"
        )

if __name__ == "__main__":
    unittest.main()
